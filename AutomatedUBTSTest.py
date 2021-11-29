from time import sleep
from time import time
import re
from mcculw import ul
import os
import numpy as np
import pandas as pd
from util import num2str, constrained_input
from constants import PIN
import serial
from matplotlib import pyplot as plt
from threading import Thread
from BrewerControl import GRID_Elite
from GridEliteController import EliteController
from MccTempMonitor import MCC_Mixed_Monitor

HEADERS = "NOTES,Predicted_Temp,Effective Target Temp,dT/dx,Estimated Temp,Measured_Temp,Flow Command,Flow Traget,Target Temp,Power Command,Flow Measured,T_offset,pwr_flow_offset,V_c2,ramp_coeff,T_in,vol"

class RoboScale:

    def __init__(self, pump_com_port, scale_com_port):
        self.pump_controller = GRID_Elite(pump_com_port, baud_rate=115200)
        self.scale_serial = serial.Serial(scale_com_port, 9600, timeout=1)
        self.pump_on = False
        self.continuous_print = False

    def turn_on_continuous_print(self):
        self.scale_serial.write('CA\r\n'.encode('UTF-8'))
        sleep(0.5)
        self.continuous_print = True

    def turn_off_continuous_print(self):
        self.scale_serial.write('0A\r\n'.encode('UTF-8'))
        sleep(0.5)
        self.continuous_print = False

    def run_pump(self):
        self.pump_controller.set_water_pump(1000)
        self.pump_on = True

    def stop_pump(self):
        self.pump_controller.set_water_pump(0)
        self.pump_on = False

    def read_all(self):
        scale_response = self.scale_serial.read_all().decode("utf-8")
        return scale_response

    def zero(self):
        self.scale_serial.write('T\r\n'.encode('UTF-8'))

    def get_state(self):
        if not self.continuous_print:
            self.turn_on_continuous_print()

        all_printouts = self.read_all()
        if '\r\n' in all_printouts:
            all_masses = re.findall('\d*\.?\d+',all_printouts)
            is_not_stable = '?' in all_printouts.split('\r\n')[-2]
            if len(all_masses) > 0:
                return float(all_masses[-1]), is_not_stable

        return None, False

    def drain_scale(self):
        self.pump_controller.set_water_pump(1000)
        mass = 1000
        empty_counter = 10
        t0 = time()
        t = 0

        while (empty_counter > 0) and (t < 240):
            mass, is_stable = self.get_state()
            t = time() - t0

            if mass is None:
                sleep(1.1)
                mass, is_stable = self.get_state()
                if mass is None:
                    self.pump_controller.set_water_pump(0)
                    raise TimeoutError('Scale failed to respond')

            if mass < 10:
                empty_counter -= 1

        sleep(4)
        self.pump_controller.set_water_pump(0)
        self.turn_off_continuous_print()


class AutomatedUBTS:

    def __init__(self, com_port, fldr_path, daq):
        self.controller = EliteController(com_port)
        self.brewer = self.controller.brewer
        self.brewer.reset()
        self.daq = daq
        sleep(1)
        self.brewer.print_europa_debug()
        sleep(1)

        self.brew_count = 0
        self.local_fldr_path = fldr_path
        self.headers = [h for h in HEADERS.split(',')]
        self.brew_data = {h:np.array([]) for h in self.headers}

    def reset_brew_data(self):
        self.brew_data = {h: np.array([]) for h in self.headers}

    def save_brew_data(self, ts, temp, size, flow_rate):
        df = pd.DataFrame(self.brew_data)

        save_str = self.local_fldr_path + '/' + num2str(ts, 0)
        for header, val in zip(['temp', 'size', 'flow_rate', 'cycle'], [temp, size, flow_rate, self.brew_count]):
            save_str += '_' + header + '-' + num2str(val, 0)
        df.to_csv(save_str + '.csv', index=0)

        return save_str

    def brew_random(self, flow_rate, brew_size, temperature):
        header_len = len(self.headers)
        brew_is_ongoing = True
        start_time = None
        last_read_time = 0
        ts = 0

        self.brewer.brew(temperature, brew_size, flow_rate)

        while brew_is_ongoing:
            try:
                response = self.brewer.read_ln()
                data = response.split(',')
                ts = time()

                if len(response) > 1:
                    print(num2str(ts) + ' ' + response)

                master_csv_ln_sans_letters = ','.join(data[1::])

                if (len(data) == header_len) and (not re.search('[a-zA-Z]', master_csv_ln_sans_letters)):
                    numeric_data = [float(x) for x in data[1::]]
                    last_read_time = ts
                    if not start_time:
                        start_time = ts

                    self.brew_data[self.headers[0]] = np.append(self.brew_data[self.headers[0]], ts)

                    for header, dat in zip(self.headers[1::], numeric_data):
                        self.brew_data[header] = np.append(self.brew_data[header], dat)

                elif len(response) > 1:
                    last_read_time = ts

                elif start_time and ((ts - last_read_time) > 10):
                    brew_is_ongoing = False
            except Exception as e:
                print(e)

        if ts:
            save_str = self.save_brew_data(ts, temperature, brew_size, flow_rate)
            pressure = True
            self.brew_count += 1

            return pressure, save_str
        else:
            print('No brew')
            return None, None

    def run_test_plan(self, daq_is_counter=True):
        test_plan_path = input('enter DOE path: ')
        test_plan = pd.read_csv(test_plan_path)

        flow_rates = test_plan.Type.values
        temps = test_plan.Temp.values
        brew_sizes = test_plan.Size.values

        for flow, temp, vol in zip(flow_rates, temps, brew_sizes):
            # Brew
            # zero daq
            if daq_is_counter:
                self.daq.zero_count = []

                for pin in self.daq.pins:
                    self.daq.zero_count.append(ul.c_in_32(0, pin))
            daq_thread = Thread(target=self.daq.run_with_sig_kill)
            daq_thread.start()
            brew_was_successful, save_str = self.brew_random(flow, vol, temp)
            input('Press any key to stop data collection')
            self.daq.keep_running = False
            daq_thread.join()
            plt.close()
            if brew_was_successful:

                plot_df = pd.DataFrame(self.brew_data)
                plot_df[['Estimated Temp', 'Measured_Temp', 'Target Temp']].plot()
                # df[['T_out']].plot()
                # plot and save plot
                figure = plt.gcf()
                plt.show(block=False)
                plt.pause(0.1)
                figure.savefig(save_str + '.png')
                self.reset_brew_data()
                input('Press any key to run next test')


class AutomatedPAMS(AutomatedUBTS):
    def __init__(self, com_port, fldr_path, daq, scale_com, k_mini_com):

        super().__init__(com_port, fldr_path, daq)
        self.scale = RoboScale('COM' + k_mini_com, 'COM' + scale_com)

    def brew_random(self, flow_rate, brew_size, temperature):
        header_len = len(self.headers)
        brew_is_ongoing = True
        start_time = None
        last_read_time = 0
        ts = 0
        brew_mass_dict = {'time':np.array([]), 'mass':np.array([])}

        self.brewer.brew(temperature, brew_size, flow_rate)
        self.scale.turn_on_continuous_print()

        while brew_is_ongoing:
            try:
                brew_mass, _ = self.scale.get_state()

                if brew_mass:
                    brew_mass_dict['mass'] = np.append(brew_mass_dict['mass'], brew_mass)
                    brew_mass_dict['time'] = np.append(brew_mass_dict['time'], time())

                    if brew_mass > 370:
                        self.scale.run_pump()
                    elif self.scale.pump_on:
                        if len(brew_mass_dict['mass']) >=11:
                            if (np.mean(brew_mass_dict['mass'][-10::]) < 200):
                                self.scale.stop_pump()
                        elif (np.mean(brew_mass_dict['mass']) < 200):
                            self.scale.stop_pump()


                response = self.brewer.read_ln()
                data = response.split(',')
                ts = time()

                if len(response) > 1:
                    print(num2str(ts) + ' ' + response)

                master_csv_ln_sans_letters = ','.join(data[1::])

                if (len(data) == header_len) and (not re.search('[a-zA-Z]', master_csv_ln_sans_letters)):
                    numeric_data = [float(x) for x in data[1::]]
                    last_read_time = ts
                    if not start_time:
                        start_time = ts

                    self.brew_data[self.headers[0]] = np.append(self.brew_data[self.headers[0]], ts)

                    for header, dat in zip(self.headers[1::], numeric_data):
                        self.brew_data[header] = np.append(self.brew_data[header], dat)

                elif len(response) > 1:
                    last_read_time = ts

                elif start_time and ((ts - last_read_time) > 20):
                    brew_is_ongoing = False
            except Exception as e:
                print(e)
                self.brewer.reset()
                sleep(1)
                self.scale.drain_scale()

        if ts:
            save_str = self.save_brew_data(ts, temperature, brew_size, flow_rate)

            brew_mass_df = pd.DataFrame(brew_mass_dict)
            brew_mass_df.to_csv(save_str + '_mass.csv')

            pressure = True
            self.brew_count += 1
            self.scale.turn_off_continuous_print()

            return pressure, save_str
        else:
            print('No brew')
            self.scale.turn_off_continuous_print()
            return None, None

    def run_test_plan(self, daq_is_counter=False, coffee_bloom=False):
        use_random_brews = constrained_input('should computer randomize brews', ('y', 'n'))

        if use_random_brews == 'y':
            flow_rates = np.array([])
            temps = np.array([])
            brew_sizes =  np.array([])
            bloom_times =  np.array([])
            bloom_volumes = np.array([])
            bloom_temps = np.array([])

            num_brews = int(input('how many brews should run: '))

            for i in range(0, num_brews):
                temperature = 195 + 18 * np.random.rand() - 9
                temps = np.append(temps, temperature)

                brew_size_optons = [2, 4]
                brew_size = brew_size_optons[np.random.randint(low=0, high=2)]
                brew_sizes = np.append(brew_sizes, brew_size)

                flow_rate_options = [5, 7, 9]
                flow_rate = flow_rate_options[np.random.randint(low=0, high=3)]
                flow_rates = np.append(flow_rates, flow_rate)

                if coffee_bloom:
                    coffee_bloom_times = [10, 15]
                    bloom_times = np.append(bloom_times, coffee_bloom_times[np.random.randint(low=0, high=2)])

                    coffee_bloom_volumes = np.arange(17, 27, 2.5)
                    bloom_volumes = np.append(bloom_volumes, coffee_bloom_volumes[np.random.randint(low=0, high=len(coffee_bloom_volumes))])

                    coffee_bloom_temps = [80, 85, 90, 95]
                    bloom_temps = np.append(bloom_temps, coffee_bloom_temps[np.random.randint(low=0, high=3)])

            if coffee_bloom:
                test_plan = pd.DataFrame({'Type':flow_rates, 'Temp':temps, 'Size':brew_sizes
                                             , 'Bloom_Time':bloom_times, 'Bloom_Volume':bloom_volumes
                                             , 'Bloom_Temp':bloom_temps})
            else:
                test_plan = pd.DataFrame({'Type': flow_rates, 'Temp': temps, 'Size': brew_sizes})
            test_plan.to_csv(self.local_fldr_path + '/' + num2str(time(), num_didgets=0) + '_generated_test_plan.csv')

        else:
            test_plan_path = input('enter DOE path: ')
            test_plan = pd.read_csv(test_plan_path)

            flow_rates = test_plan.Type.values
            temps = test_plan.Temp.values
            brew_sizes = test_plan.Size.values
            if coffee_bloom:
                bloom_times = test_plan.Bloom_Time.values
                bloom_volumes = test_plan.Bloom_Volume.values
                bloom_temps = test_plan.Bloom_Temp.values

        for i in range(0, len(flow_rates)):
            flow = flow_rates[i]
            temp = temps[i]
            vol = brew_sizes[i]

            if coffee_bloom:
                self.brewer.coffee_bloom_parameters(bloom_times[i], bloom_volumes[i])
                sleep(0.1)
                self.brewer.coffee_bloom_temp(bloom_temps[i])
                sleep(0.1)
            # Brew
            # zero daq
            if daq_is_counter:
                self.daq.re_zero()
            daq_thread = Thread(target=self.daq.run_with_sig_kill)
            daq_thread.start()
            brew_was_successful, save_str = self.brew_random(flow, vol, temp)
            sleep(10)
            self.daq.keep_running = False

            self.scale.drain_scale()

            brew_mass_not_stable = True
            while brew_mass_not_stable:
                _, brew_mass_not_stable = self.scale.get_state()
                sleep(1)
                print('waiting for stability')
            print('stable')
            self.scale.turn_off_continuous_print()

            daq_thread.join()
            plt.close()
            if brew_was_successful:
                # plot_df = pd.DataFrame(self.brew_data)
                # brew_ax = plot_df[['Estimated Temp', 'Measured_Temp', 'Target Temp']].plot()
                # brew_fig = brew_ax.get_figure()
                # plt.title('Brew Data')
                #
                # ubts_volume_ax = self.daq.data_df.Volume.plot()
                # ubts_volume_fig = ubts_volume_ax.get_figure()
                # plt.title('UBTS Volume Data')
                #
                # ubts_opto_ax = self.daq.data_df.Opto_Probe.plot()
                # ubts_opto_fig = ubts_opto_ax.get_figure()
                # plt.title('UBTS Opto Sensor Data')

                ubts_temp_ax = self.daq.data_df[['Entrance_Needle', 'Exit_Needle', 'In_Cup']].plot()
                ubts_temp_fig = ubts_temp_ax.get_figure()
                plt.title('UBTS Temperature Data')



                plt.show(block=False)
                plt.pause(0.1)
                ubts_temp_fig.savefig(save_str + '_ubts_temp.png')
                # ubts_volume_fig.savefig(save_str + '_ubts_vol.png')
                # ubts_opto_fig.savefig(save_str + '_ubts_opto.png')
                # brew_fig.savefig(save_str + '.png')
                self.reset_brew_data()

                if not self.brew_count % 5:
                    self.scale.run_pump()
                    self.controller.cool_heater()
                    self.scale.stop_pump()
                    sleep(1)
                    self.brewer.print_europa_debug()
                    sleep(1)




if __name__=="__main__":
    Port = '28'#input('What COM port: ')
    save_fldr = input('enter the save folder: ')
    mcc = MCC_Mixed_Monitor((0, 1, 2), (1, 1, 1),
                      ('Entrance_Needle', 'Exit_Needle', 'In_Cup'),
                      save_fldr + '//', (None, None, None),
                      (PIN.TEMP_PIN, PIN.TEMP_PIN, PIN.TEMP_PIN))
    auto_test = AutomatedPAMS('COM' + Port, save_fldr, mcc, '33', '7')
    auto_test.run_test_plan(coffee_bloom=True)

