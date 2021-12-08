# -*- coding: utf-8 -*-
"""
Created on 11/23/2021

@author: Riccardo Vietri

"""
import numpy as np
import re
import time
import pandas as pd
import os
import matplotlib.pyplot as plt

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Function definition for common utilities
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def import_UBTS(file):
    try:
        # Import the text file (tab delimited)
        data = pd.read_csv(file, sep='\t', skiprows=66)
    except:
        print('Empty Dataframe: ' + file)
        data = pd.DataFrame()
    f = open(file, "r")
    lines = f.readlines()
    notes = (lines[61])
    # Rename columns based on known headers
    data.columns = [
        'Sample Time (s)',
        'T entrance needle (degF)',
        'T exit stream (degF)',
        'T AUX (degF)',
        'T in-cup (degF)',
        'AUX sensor (psig)',
        'Brew Mass (g)',
        'Brewer Current (Arms)',
        'ARxBrewerV (ml)',
        'ARxBrewerT (degF)',
        'ARxBrewerP (pressure)',
        'ARxBrewerF (ml/sec)',
        'EN Synced Temp (degF)',
        'EN Synced Mass (degF)',
        'ES Synced Temp (degF)',
        'EN Synced Mass (degF)'
    ]

    # drop nan columns
    data = data.dropna(axis=1)
    if data['Sample Time (s)'].iloc[-1] == 'Sample Time (s)':
        print('Dropping last row for file: ' + file)
        data.drop(data.tail(1).index, inplace=True)  # drop last row

    return data, notes


def plottemps(plots_dir, filename, df):
    fig2, ax2 = plt.subplots()
    plt.plot(df['Brew Mass (g)'], df['T entrance needle (degF)'], label='Entrance Needle')
    plt.plot(df['Brew Mass (g)'], df['T exit stream (degF)'], label='Exit Needle')
    plt.plot(df['Brew Mass (g)'], df['T in-cup (degF)'], label='In-Cup')
    ax2.legend(loc=0)
    ax2.grid()
    ax2.set_xlabel("Brew Mass (g)")
    ax2.set_ylabel(r"Temp (F)")
    plt.title("Temp vs Brew Mass " + filename[-13:-4])
    plt.xlim([0, 180])
    fig2.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = plots_dir + '\PlotTemps' + filename[-12:-4] + '.png'
    fig2.savefig(figure_path)  # save the figure to file
    plt.close(fig2)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Main program function
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def main():
    # Begin timing how long the script takes
    t0 = time.time()
    rootdir = r"C:\Users\VIERX716\OneDrive - KDP\Documents\Coffee Bloom\UBTS005\DRIP_DOE"
    # Results Directory
    results_dir = os.path.join(rootdir, 'Results')
    # Plots Directory
    plots_dir = os.path.join(results_dir, 'Plots')
    drip_dir = os.path.join(plots_dir, 'Drip')

    # Create a Results folder to save images and the files
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print('\nCreating Results Folder: \n')

    else:
        print('\nResults Folder: \n')
    print(results_dir)

    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    if not os.path.exists(drip_dir):
        os.makedirs(drip_dir)

    path, dirs, files = next(os.walk(rootdir))
    file_count = len(files)
    bloom_temps = [0] * file_count
    bloom_times = [0] * file_count
    bloom_vols = [0] * file_count
    tests = [0] * file_count
    brew_code = [""] * file_count
    drip_steam = [0] * file_count
    drip_vols = [0] * file_count
    pump_disp = [0] * file_count
    max_temp = [0] * file_count
    # Amount of volume that exists before PM after rinse and purge
    rinse_avg_prefill = np.mean([8.9, 8.9, 8.8])
    print("Rinse Average Prefill: "+str(rinse_avg_prefill))
    # Amount of volume before PM after regular brew and purge
    regular_avg_prefill = np.mean([11.6, 10.3, 10.4, 10.2])
    print("Brew Average Prefill: "+str(regular_avg_prefill))
    drip_temps = [0] * file_count
    brew_num = [0] * file_count
    brew_size = [0] * file_count
    flow_rate = [0] * file_count
    flow_rate_command = [0] * file_count
    js = []
    dfs = {}

    # step through data directory looking for UBTS files
    for subdir, dirs, files in os.walk(rootdir):

        if not ((subdir == results_dir) or (subdir == plots_dir) or (subdir == drip_dir)):
            for i in range(len(files)):
                file = files[i]
                UBTS_filename = rootdir + '\\' + file

                if (file[-11:-6] == 'Cycle') or (file[-12:-7] == 'Cycle') or (file[-13:-8] == 'Cycle'):
                    if file[-7:-4].isnumeric():
                        number = file[-7:-4]
                    elif file[-6:-4].isnumeric():
                        number = file[-6:-4]
                    else:
                        number = file[-5:-4]
                    # Ratchet way to compensate for the fact that sometimes we're missing cases and that's ok
                    if tests[i - 2] != (int(number) - 1):
                        skipped_test = True
                        tests[i] = (int(number) - 1 * 0)
                    else:
                        tests[i] = (int(number))
                    if tests[i] != 1:
                        df, notes = import_UBTS(UBTS_filename)

                        if "PULSE" in notes:
                            brew_code[i] = ['Pulse']
                        else:
                            brew_code[i] = ['Europa']

                        dfs['t' + str(tests[i])] = df.shift(i).add_suffix('_t' + str(tests[i]))

                        plottemps(plots_dir, UBTS_filename, df)

                        t = np.array(df['Sample Time (s)'])
                        brew_mass = np.array(df['Brew Mass (g)'])
                        brew_mass_theory = np.array(df['ARxBrewerV (ml)'])
                        d1 = np.diff(brew_mass) / np.diff(t)
                        d2 = np.diff(brew_mass_theory) / np.diff(t)
                        # Take rolling average, with a window size of 3
                        ret = np.cumsum(d1, dtype=float)
                        ret2 = np.cumsum(d2, dtype=float)
                        ret[3:] = ret[3:] - ret[:-3]
                        ret2[3:] = ret2[3:] - ret2[:-3]
                        start = [idx for idx, element in enumerate(ret) if (element >= 0.1) and (t[idx] >= 4)]
                        start2 = [idx2 for idx2, element2 in enumerate(ret2) if (element2 >= 0.1) and (t[idx2] >= 4)]
                        idx0 = start[0]
                        idx2_0 = start2[0]
                        end = [id for id, element in enumerate(ret) if (element <= 0) and (id > idx0)]
                        idx_end = end[0]
                        end2 = [id2 for id2, element2 in enumerate(ret2) if (element2 <= 0) and (id2 > idx2_0)]
                        idx2_end = end2[0]
                        drip_volume_t = brew_mass_theory[idx2_end] - brew_mass_theory[idx2_0]
                        drip_time_t = t[idx2_end] - t[idx2_0]

                        drip_volume = brew_mass[idx_end] - brew_mass[idx0]
                        drip_time = t[idx_end] - t[idx0]

                        flow_rate[i] = 60*drip_volume/drip_time
                        flow_rate_command[i] = 60 * drip_volume_t / drip_time_t

                        if tests[i]>268:
                            fig, ax = plt.subplots()
                            d1a = np.append(d1, 0)
                            avg = np.append(ret, 0)
                            ax.plot(t, d1a,
                                     label='Derivative')
                            ax.plot(t, avg, 'g',
                                    label='Derivative Averaged')
                            ax.plot(t[idx0], 0.25, 'b*',
                                    label='Start')
                            ax.plot(t[idx_end], 0.25, 'bd',
                                    label='End')
                            ax2 = ax.twinx()
                            ax2.plot(t, brew_mass, 'r',
                                     label='brew mass')
                            ax.set_xlim([0, 25])
                            ax.set_ylim([0, 0.5])
                            ax2.set_ylim([0, 15])
                            ax.set_ylabel('Derivative label')
                            ax2.set_ylabel('Brew Mass label')
                            ax.legend(loc=0)
                            fig.show()
                            ax.grid()
                            plt.close(fig)
                    else:
                        bloom_times[i] = 20
                        bloom_vols[i] = 15
                        bloom_temps[i] = 80
                # collect bloom variables used in this test using log file
                elif file[-7:-4] == 'log' and (tests[i-1] != 1):
                    js.append(i)
                    parameters = ['Temp:', 'Time:', 'Volume:', 'Size_Selected']
                    # read the log with multiple delimiters
                    with open(UBTS_filename) as fobj:
                        for line in fobj:
                            line_data = re.split('\t|\n|,|[|]', line)
                            # using list comprehension
                            # checking if string contains list element
                            if parameters[0] in line:
                                line_list = re.split(':|,| |\t|\n', line)
                                bloom_temps[i - 1] = (float(line_list[-2]))
                            elif parameters[1] in line:
                                line_list = re.split(':|,| |\t|\n', line)
                                bloom_times[i - 1] = (float(line_list[-6]))
                                bloom_vols[i - 1] = (float(line_list[-2]))
                            elif parameters[3] in line:
                                line_list = re.split(':|,| |\t|\n', line)
                                brew_size[i - 1] = (float(line_list[-3]))
                    # find the closest datapoint to the 5 seconds after the bloom time for this cycle
                    if (tests[i-1] != 0) and (bloom_times[i-1] != 0):
                        df = dfs['t' + str(tests[i-1])]
                        drip_idx = abs(df['Sample Time (s)_t' + str(tests[i-1])] - (bloom_times[i-1] + 5)).idxmin()
                        drip_begin_idx = abs(df['Sample Time (s)_t' + str(tests[i - 1])] - (bloom_times[i - 1] - 5)).idxmin()
                        # Drip mass is found at the index ~= bloom time + 5 seconds
                        drip_mass = df['Brew Mass (g)_t' + str(tests[i-1])][drip_idx]
                        drip_temp = df['T entrance needle (degF)_t' + str(tests[i-1])][drip_idx]
                        # find the average drip mass around this time
                        avg_drip_mass = df['Brew Mass (g)_t' + str(tests[i-1])].rolling(2).mean()[drip_idx]
                        avg_drip_temp = df['T entrance needle (degF)_t' + str(tests[i - 1])][drip_begin_idx:drip_idx].mean()
                        '''
                        fig, ax = plt.subplots()
                        ax.plot(df['Sample Time (s)_t' + str(tests[i-1])], df['T entrance needle (degF)_t' + str(tests[i-1])], label='Entrance Needle')
                        ax.plot(df['Sample Time (s)_t' + str(tests[i-1])][drip_idx], drip_temp, marker = 'o', ms = 10, label='Probe pt')
                        ax.plot(df['Sample Time (s)_t' + str(tests[i - 1])][drip_begin_idx], avg_drip_temp, marker='o', ms=10,
                                label='Probe pt2')
                        ax2 = ax.twinx()
                        ax2.plot(df['Sample Time (s)_t' + str(tests[i-1])], df['Brew Mass (g)_t' + str(tests[i-1])], color='r', label='Brew Mass')
                        ax2.plot(df['Sample Time (s)_t' + str(tests[i - 1])][drip_idx],df['Brew Mass (g)_t' + str(tests[i-1])][drip_idx], color='g',marker='o', ms=10,
                                label='point probe')
                        ax.legend(loc=0)
                        ax2.legend(loc=2)
                        ax.set_xlabel("Sample Time (s)")
                        ax.set_ylabel(r"Temp (F)")
                        ax2.set_ylabel(r"Brew Mass (g)")
                        plt.title("Temp vs Brew Mass Cycle " + str(tests[i-1]))
                        plt.xlim([0, 30])
                        ax2.set_ylim([0, 25])
                        plt.show()
                        plt.close(fig)
                        '''
                        # if average brew mass at this point is not consistent, enter zero for debugging
                        if not (drip_mass < avg_drip_mass * 1.1) and (drip_mass > avg_drip_mass * 0.9):
                            avg_drip_mass = 0
                            print('Average Drip Mass Not within Limits, idx: ' + str(i) + " test#: " + str(tests[i-1]))
                            print('Average Drip Mass: ' + str(avg_drip_mass))
                            print('Local Drip Mass: ' + str(drip_mass))
                        # collect drip volume
                        drip_vols[i-1] = avg_drip_mass
                        drip_temps[i-1] = avg_drip_temp
                        max_temp[i-1] = df['T entrance needle (degF)_t' + str(tests[i - 1])][0:drip_idx].max()
                        brew_num[i-1] = (tests[i-1]-1) % 3
                        if (tests[i-1]-1) % 3 == 0:
                            pump_disp[i - 1] = avg_drip_mass + rinse_avg_prefill
                        else:
                            pump_disp[i - 1] = avg_drip_mass + regular_avg_prefill
                else:
                    js.append(i)

    for j in sorted(js, reverse=True):
        del tests[j]
        del brew_code[j]
        del brew_size[j]
        del drip_vols[j]
        del drip_temps[j]
        del max_temp[j]
        del pump_disp[j]
        del brew_num[j]
        del flow_rate[j]
        del flow_rate_command[j]
        del bloom_temps[j]
        del bloom_vols[j]
        del bloom_times[j]

    d = {'Test Number': tests,
         'Brew Code': brew_code,
         'Brew Size': brew_size,
         'Drip Vol (mL)': drip_vols,
         'Drip Temp (F)': drip_temps,
         'Max Drip Temp (F)': max_temp,
         'Water Displaced by Pump (mL)': pump_disp,
         'Brew Number': brew_num,
         'Pre-Infusion Flow Rate (mL/min)': flow_rate,
         'Pre-Infusion Flow Rate Command Avg (mL/min)': flow_rate_command,
         'Bloom Temp (F)': bloom_temps,
         'Bloom Time (s)': bloom_times,
         'Bloom Volume (ml)': bloom_vols,
         }

    df_stats = pd.DataFrame(data=d)

    Brew_Stats = rootdir + "\\" + 'Results' + "\\" + 'Brew Stats.csv'
    df_stats.to_csv(Brew_Stats, encoding='utf-8', index=False)
    print(df_stats.iloc[:,3:6])
    # plot all UBTS Cases


if __name__ == "__main__":
    main()
