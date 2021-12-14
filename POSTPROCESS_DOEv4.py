# -*- coding: utf-8 -*-
"""
Created on 11/23/2021

@author: Riccardo Vietri

"""
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
import re
import time
import pandas as pd
import os
import matplotlib.pyplot as plt
from scipy import stats
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Function definition for common utilities
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def is_float(element) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Main program function
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def main():
    # Begin timing how long the script takes
    t0 = time.time()
    rootdir = r"C:\Users\VIERX716\OneDrive - KDP\Documents\Coffee Bloom\DOE v4\Pump_Testing"
    # Results Directory
    results_dir = os.path.join(rootdir, 'Results')
    # Plots Directory
    plots_dir = os.path.join(results_dir, 'Plots')
    tests_dir = os.path.join(results_dir, 'Test')

    # Create a Results folder to save images and the files
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print('\nCreating Results Folder: \n')
    else:
        print('\nResults Folder: \n')
    print(results_dir)

    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)

    tests = []
    voltages = []
    voltage_times = []
    pump_flow_rates = []
    final_masses = []
    initial_masses = []
    pump_flow_times = []
    pump_flow_over_v = []
    pump_t = []
    EN_temps = []
    ES_temps = []

    df = pd.DataFrame()
    dfs = {}
    dfs['t0'] = df
    # step through data directory looking for UBTS files
    for subdir, dirs, files in os.walk(rootdir):
        if ((subdir == rootdir)):

            for i in range(len(files)):
                mass = []
                m_time = []
                voltage = 0
                pump_flow_rate = 0
                voltage_time = 0
                end_mass = 0
                initial_mass = 0

                file = files[i]
                filename = rootdir + '\\' + file
                if (file[-4:] == '.log'):
                    if file[-7:-4].isnumeric():
                        number = file[-7:-4]
                    elif file[-8:-5].isnumeric():
                        number = file[-8:-5]
                    else:
                        number = file[-9:-6]
                    with open(filename) as fobj:
                        prev_time = 0
                        smooth_window = 8
                        for line in fobj:
                            line_data = re.split('\t|\n|,| |]', line)
                            for j in range(len(line_data)):
                                if (is_float(line_data[j])):
                                    try:
                                        prev_time = float(line_data[1][-6:])
                                    except:
                                        print("Unable to get mass data from file " + str(filename))
                                        print((line_data[1][-6:]))
                                    m_time.append(prev_time)
                                    mass.append(float(line_data[j]))

                    try:
                        df_scale = pd.DataFrame({'Time': m_time, 'Mass': mass})
                        df_scale['Smooth_Mass'] = df_scale.Mass.rolling(smooth_window).mean()
                        if (df_scale.Time[1] - df_scale.Time[0]) > 10:
                            t0 = 0
                        else:
                            t0 = df_scale.Time[0]
                        df_scale.Time = df_scale.Time - (t0 + 1)
                        for ii in range(len(df_scale.Time)-1):
                            if (df_scale.Time[ii+1] < df_scale.Time[ii]-50):
                                df_scale.Time[ii+1] = df_scale.Time[ii+1]+60
                        df_scale = df_scale.iloc[1: , :]

                        x = df_scale.Time.to_numpy()
                        y = df_scale.Mass.to_numpy()
                        y2 = df_scale.Smooth_Mass.to_numpy()
                        dx = x[1] - x[0]
                        dydx = np.gradient(y, dx)
                        df_scale['Mass_Gradient'] = dydx
                        if not x.all():
                            np.nan_to_num(x)
                        if not y.all():
                            np.nan_to_num(y)
                        if not y2.all():
                            np.nan_to_num(y2)
                        diff = np.diff(y) / np.diff(x)
                        diff = np.append(diff, 0)
                        df_scale['Mass_Diff'] = diff
                        diff2 = np.diff(y2) / np.diff(x)
                        diff2 = np.append(diff2, 0)
                        df_scale['Smooth_Mass_Diff'] = diff2
                        difference = df_scale.diff(axis=0)
                        # Add column of df_scale where the difference between consecutive mass data is stored
                        df_scale['Mass_Gradient_Delta'] = difference.Mass_Gradient
                        df_scale['Mass_Diff_Delta'] = difference.Mass_Diff
                        df_scale['Smooth_Mass_Diff_Delta'] = difference.Smooth_Mass_Diff
                        df_scale['Mass_Delta'] = difference.Mass
                        difference2 = df_scale.diff(axis=0)
                        # Add column of df_scale where the difference between consecutive mass data is stored
                        df_scale['Mass_Gradient_Delta2'] = difference2.Mass_Gradient_Delta
                        df_scale['Mass_Diff_Delta2'] = difference2.Mass_Diff_Delta
                        df_scale['Smooth_Mass_Diff_Delta2'] = difference2.Smooth_Mass_Diff_Delta
                        df_scale['Mass_Delta2'] = difference2.Mass_Delta
                        df_scale_stable = df_scale[df_scale['Mass_Delta2'].between(-0.2, 0.2)]
                        # remove significant outliers based on change in mass
                        # https://stackoverflow.com/questions/61815114/deleting-entire-rows-of-a-dataset-for-outliers-found-in-a-single-column
                        dfn_scale_stable = df_scale_stable[(np.abs(stats.zscore(df_scale_stable['Mass_Delta'])) < 3)]
                    except:
                        print('Failed log file for file: '+str(file))
                        number = '0'
                # Otherwise the file is part of the labview output
                elif (file[-4:] == '.lvm'):
                    df = pd.read_csv(filename, sep='\t', skiprows=23, header=0)
                    size_df = len(df.X_Value)
                    n_time =1+(df.X_Value.max()*1000)
                    times_NI = np.linspace(0, (1/n_time)*size_df, size_df)
                    df['Time'] = times_NI
                    df_nonNAN = df.dropna()
                    df_nonNAN = df[df['Untitled'].notna()]
                    t_pump = df_nonNAN.Untitled[0]
                    pump_t.append(t_pump)
                    if file[-9:-6].isnumeric():
                        number_NI = file[-9:-6]
                    elif file[-8:-5].isnumeric():
                        number_NI = file[-8:-5]
                    else:
                        number_NI = file[-7:-4]

                if not df.empty and (int(number) == int(number_NI)):
                    # Collect dataframe rows with only voltages over 0.1 V
                    non_zero_voltages = df[(df.Voltage > 0.1)]
                    try:
                        # The time the voltage was nonzero is the difference between the first and last datapoints of the above
                        voltage_time = non_zero_voltages.Time.iloc[-1]-non_zero_voltages.Time.iloc[0]
                        df.Time = df.Time - non_zero_voltages.Time.iloc[0]
                        df = df[df.Time >= -0.5]
                    except:
                        print("Unable to get Voltage Time")
                        print(file)
                    # The voltages should be fairly consistent, so take the average voltage
                    voltage = non_zero_voltages.Voltage.mean()

                    try:
                        EN_temp = non_zero_voltages.Temperature.mean()
                        ES_temp = non_zero_voltages.Temperature_0.mean()
                    except:
                        try:
                            EN_temp = non_zero_voltages.T1.mean()
                            ES_temp = non_zero_voltages.T2.mean()
                        except:
                            EN_temp = 0
                            ES_temp = 0

                    # Collect rows of dataframe where the mass and the change in mass were positive
                    non_zero_mass = df_scale.loc[(df_scale['Mass']>=0) & (df_scale['Mass_Delta'] > 0)]
                    #mass_time = non_zero_mass.Time.iloc[-1] - non_zero_mass.Time.iloc[0]
                    #Final_Mass = non_zero_mass.Smooth_Mass.iloc[-1]

                    # Filter out results where the gradient and difference between mass data are two high
                    df_scale_f1 = df_scale[df_scale['Mass_Gradient'].between(-0.01, 0.01)]
                    df_scale_f2 = df_scale_f1[df_scale_f1['Mass_Diff'].between(-0.01, 0.01)]
                    df_scale_resetidx = df_scale_f2.reset_index()
                    # Take the difference between each row in filtered df
                    df_f2 = df_scale_f2.diff(axis=0)
                    #df_f2 = df_f2.dropna()
                    # Sort in descedning order to find largest jump in mass
                    df_f2_sorted = df_f2.sort_values(by=['Mass'], ascending=False)

                    end_idx = df_f2_sorted.index[0]
                    idx_list = df_scale_resetidx.index[df_scale_f2.index == end_idx].tolist()
                    begin_idx = df_scale_resetidx['index'][idx_list[0]-1]
                    end_mass = df_scale.Mass[end_idx]
                    #end_mass_time = df_scale.Time[end_idx]
                    # Drip mass is found at the index ~= bloom time + 5 seconds
                    initial_mass = df_scale['Mass'][begin_idx]
                    pump_flow_rate = (end_mass - initial_mass)/(df_scale.Time[end_idx] - df_scale['Time'][begin_idx])

                    '''
                    print("Test")
                    print(number)
                    print("Final Mass")
                    print(Final_Mass)
                    print("Mass At End of Pump Flow")
                    print(end_mass)
                    print("Mass at Beginning of Pump Flow")
                    print(initial_mass)
                    print("Pump Flow Rate (mL/s)")
                    print("{:.2f}".format(pump_flow_rate))
                    print("Pump Flow Rate (mL/min)")
                    print("{:.2f}".format(pump_flow_rate*60))
                    print("Average Pump Voltage")
                    print("{:.2f}".format(voltage))
                    print("Time change in voltage")
                    print("{:.2f}".format(voltage_time))
                    '''
                    # Collect pertinent data
                    if (int(number) not in tests):
                        tests.append(int(number))
                        voltages.append(voltage)
                        voltage_times.append(voltage_time)
                        pump_flow_rates.append(pump_flow_rate*60)
                        final_masses.append(end_mass)
                        initial_masses.append(initial_mass)
                        pump_flow_times.append((df_scale.Time[end_idx] - df_scale['Time'][begin_idx]))
                        pump_flow_over_v.append(pump_flow_rate*60/voltage)
                        EN_temps.append(EN_temp)
                        ES_temps.append(ES_temp)

                    try:
                        t0_mass = df_scale_stable.Time[begin_idx]
                        df_scale_stable.Time = df_scale_stable.Time - (t0_mass)
                        df_scale_stable = df_scale_stable[df_scale_stable.Time>0]
                    except:
                        print('Non-zeros mass time')


                    fig, ax = plt.subplots()
                    color = 'tab:red'
                    ax.set_xlabel('Time (s)')
                    ax.tick_params(axis='y', labelcolor=color)
                    ax.set_ylabel('Voltage', color=color)
                    lns1 = ax.plot(df.Time, df.Voltage, label='Voltage', color=color)

                    ax2 = ax.twinx()
                    lns2 = ax2.plot(df_scale_stable.Time, df_scale_stable.Mass, label='Mass', color='blue')
                    #lns3 = ax2.plot(df_scale_stable.Time, df_scale_stable.Mass,  label='Mass', color='green')
                    # added these three lines
                    #labs = [l.get_label() for l in lns]
                    ax.legend(loc=1)
                    ax2.legend(loc=4)
                    color = 'tab:blue'

                    ax2.set_ylabel('Mass (g)', color=color)  # we already handled the x-label with ax
                    ax2.tick_params(axis='y', labelcolor=color)
                    ax.grid()
                    plt.title("Temp vs Brew Mass - Test " + str(number))
                    fig.tight_layout()  # otherwise the right y-label is slightly clipped
                    figure_path = plots_dir + '\Test' + str(number)+'.png'
                    fig.savefig(figure_path)  # save the figure to file
                    plt.close(fig)

    d = {'Test Number': tests,
         'Pump Voltage (V)': voltages,
         'Pump Flow Rate (ml/min)': pump_flow_rates,
         'Pump Flow Per volt (mL/min*V)': pump_flow_over_v,
         'Initial Cup Mass (g)': initial_masses,
         'Final Cup Mass (g)': final_masses,
         'Voltage Time (s)': voltage_times,
         'Pump Flow Time (s)': pump_flow_times,
         'Pump Specified Flow Time (s)': pump_t,
         'EN Temp (F)': EN_temps,
         'ES Temp (F)': ES_temps
         }

    df_stats = pd.DataFrame(data=d)
    Pump_stats = results_dir + "\\" + 'Pump Stats.csv'
    df_stats.to_csv(Pump_stats, encoding='utf-8', index=False)
    print(df_stats)

if __name__ == "__main__":
    main()
