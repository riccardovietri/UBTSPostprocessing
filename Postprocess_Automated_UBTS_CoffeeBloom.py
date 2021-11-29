# -*- coding: utf-8 -*-
"""
Created on 10/15/2021

@author: Riccardo Vietri

Post-processing script for Automated UBTS data.
Plots Brew mass and time data both individually and together
Calculated drip mass and temperature for coffee bloom runs
"""
import numpy as np
import re
import time
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Function definition for common utilities
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def plot_mass(mass_data, plots_dir, cycle_num):

    fig, ax = plt.subplots()
    plt.plot(mass_data['time'], mass_data['mass'], label='Data')
    ax.legend(loc=0)
    ax.grid()
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(r"Brew Mass (g)")
    plt.title("Brew Mass vs Time for cycle " + str(cycle_num))
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = plots_dir + '\BrewVsTime_cycle_' + str(cycle_num)+'.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

def plot_temp(temp_data, plots_dir, cycle_num):
    fig, ax = plt.subplots()
    ax.set_ylabel('Temperature (F)')
    ax.set_xlabel('Time (s)')
    plt.plot(temp_data['Time (s)'], temp_data['Entrance_Needle'], label='Entrance Needle')
    plt.plot(temp_data['Time (s)'], temp_data['Exit_Needle'], label='Exit Needle')
    plt.plot(temp_data['Time (s)'], temp_data['In_Cup'], label='In-Cup')
    ax.legend(loc=0)
    ax.grid()
    plt.title("Temp vs Time for cycle " + str(cycle_num))
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = plots_dir + '\TempVsTime_cycle_' + str(cycle_num) + '.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

def plot_temp_mass(temp_data, mass_data, plots_dir, cycle_num):
    fig, ax1 = plt.subplots()
    color = 'tab:red'
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Brew Mass (g)', color=color)
    ax1.plot(mass_data['time'], mass_data['mass'], label='Mass', color = color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Temp', color=color)  # we already handled the x-label with ax1
    ax2.plot(temp_data['Time (s)'],temp_data['Entrance_Needle'], label = 'Entrance Needle')
    ax2.plot(temp_data['Time (s)'],temp_data['Exit_Needle'], label = 'Exit Needle')
    ax2.plot(temp_data['Time (s)'],temp_data['In_Cup'], label = 'In-Cup')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title("Temp and Mass vs Time for cycle " + str(cycle_num))
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = plots_dir + '\Temp+MassVsTime_cycle_' + str(cycle_num) + '.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Main program function
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def main(rootdir):
    # Initialize Variables
    # Number of cycles after which rinse and reset was performed
    n_cycles_rinse = 5
    # Initialize cycle number as zero, overwritten with each masss file
    cycle_num = 0
    # Initialize counter for drip_volumes as zero
    j = 0
    t_end = 0
    # Begin timing how long the script takes
    t0 = time.time()
    # Results Directory
    results_dir = os.path.join(rootdir, 'Results')
    # Plots Directory
    plots_dir = os.path.join(results_dir, 'Plots')

    # Create a Results folder to save result files
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # Create a plots folder to save plots
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)

    # step through data directory looking for  files
    for subdir, dirs, files in os.walk(rootdir):
        # so long as the results or plots subdirectory is not being investigated, search files
        if not ((subdir == results_dir) or (subdir == plots_dir)):
            # Iterate through files
            for file in files:
                # Collect this file's name and path
                UBTS_filename = rootdir + '\\' + file

                # Collect test plan data
                if "plan" in file[-10:-4]:
                    test_plan = pd.read_csv(UBTS_filename)
                    test_plan.columns = [
                        'Test Number',
                        'Flow Rate',
                        'Brew Temp',
                        'Brew Size',
                        'Bloom Time',
                        'Bloom Volume',
                        'Bloom Temp'
                    ]
                    # initialize number of tests, drip volume, and drip temperatures for each test
                    num_tests = len(test_plan)
                    drip_vols = [0] * num_tests
                    drip_temps = np.zeros((num_tests, 3))

                # Collect command data
                elif "cycle" in file[-15:-6]:
                    cycle_data = pd.read_csv(UBTS_filename)
                # Collect mass data
                elif "mass" in file[-15:-4]:
                    # Read in mass data from csv
                    mass_data = pd.read_csv(UBTS_filename)
                    # Collect cycle number, whether 1, 2, 3, or 4 digits
                    if UBTS_filename[-13:-9].isnumeric():
                        cycle_num = int(UBTS_filename[-13:-9])
                    elif UBTS_filename[-12:-9].isnumeric():
                        cycle_num = int(UBTS_filename[-12:-9])
                    elif UBTS_filename[-11:-9].isnumeric():
                        cycle_num = int(UBTS_filename[-11:-9])
                    elif UBTS_filename[-10:-9].isnumeric():
                        cycle_num = int(UBTS_filename[-10:-9])
                    # Normalize mass and time to start at 0 at first data point
                    mass_data['mass'] = mass_data['mass'] - mass_data['mass'][0]
                    t_begin_mass = mass_data['time'][0]
                    t_end_mass = mass_data['time'].iloc[-1]
                    mass_data['time'] = mass_data['time'] - t_begin_mass
                    # so long as the flow was not reset (every n runs), plot mass data
                    if not (cycle_num % n_cycles_rinse == 0):
                        # Collect the bloom time for this run using the test plan
                        bloom_time = test_plan['Bloom Time'][cycle_num]
                        # averaging window and threshold to identify outliers
                        window = 10
                        threshold = 5
                        mass_data['smoothened'] = mass_data['mass'].rolling(window, center=True).mean()
                        # collect the difference between the smoothened and actual data to identify outliers
                        difference = np.abs(mass_data['mass'] - mass_data['smoothened'])
                        # indices which are outliers and reverse of this, indices within threshold
                        outlier_idx = difference > threshold
                        within_threshold = [not elem for elem in outlier_idx]

                        # remove outliers from mass data
                        mass_data = mass_data[within_threshold]
                        # find the closest datapoint to the 5 seconds after the bloom time for this cycle
                        df_closest = mass_data.iloc[(mass_data['time'] - (bloom_time + 5)).abs().argsort()[:2]]
                        drip_idx = df_closest.index.tolist()[0]
                        # Drip mass is found at the index ~= bloom time + 5 seconds
                        drip_mass = mass_data['mass'][drip_idx]
                        # find the average drip mass around this time
                        avg_drip_mass = mass_data['mass'].rolling(2).mean()[drip_idx]

                        # if average brew mass at this point is not consistent, enter zero for debugging
                        if not (drip_mass < avg_drip_mass * 1.1) and (drip_mass > avg_drip_mass * 0.9):
                            avg_drip_mass = 0
                        # collect drip volume
                        drip_vols[j] = avg_drip_mass
                        # plot series of mass vs time figures for each cycle
                        plot_mass(mass_data, plots_dir, cycle_num)

                # Collect temp data
                elif "daq" in file[-10:-4]:
                    print("Processing cycle " + str(cycle_num))
                    temp_data = pd.read_csv(UBTS_filename)
                    t_end = float(file[0:10])
                    t_end_diff = t_end - t_end_mass
                    mass_data['time'] = mass_data['time'] + t_end_diff
                    # so long as the flow was not reset (every n runs), plot mass data
                    if not (cycle_num % n_cycles_rinse == 0):

                        #plot_temp(temp_data, plots_dir, cycle_num)
                        plot_temp_mass(temp_data, mass_data, plots_dir, cycle_num)
                        # find the closest datapoint to the 5 seconds after the bloom time for this cycle
                        temp_closest = temp_data.iloc[(temp_data['Time (s)'] - (bloom_time + 5)).abs().argsort()[:2]]
                        drip_temp_idx = temp_closest.index.tolist()[0]
                        # Drip temperature is found at the index ~= bloom time + 5 seconds
                        EN_drip_temp = temp_data.loc[drip_temp_idx-20:drip_temp_idx+20, 'Entrance_Needle'].max()
                        ES_drip_temp = temp_data.loc[drip_temp_idx-20:drip_temp_idx+20, 'Exit_Needle'].max()
                        IC_drip_temp = temp_data.loc[drip_temp_idx-20:drip_temp_idx+20, 'In_Cup'].max()

                        # collect drip volume
                        drip_temps[j] = [EN_drip_temp, ES_drip_temp, IC_drip_temp]
                    # Increase the counter now that drip volumes and temps have been recorded
                    j = j + 1
            # Add drip columns to test plan
            test_plan['drip'] = drip_vols
            test_plan['Pre-fill'] = test_plan['Bloom Volume'] - test_plan['drip']
            test_plan['Num B2B run'] = test_plan['Test Number'] % n_cycles_rinse
            test_plan['Drip EN Temp'] = drip_temps[:, 0]
            test_plan['Drip ES Temp'] = drip_temps[:, 1]
            test_plan['Drip IC Temp'] = drip_temps[:, 2]
            # As every 5th run is problematic due to rinse, remove every 5th test
            test_plan_actual = test_plan[test_plan['Test Number'] % n_cycles_rinse != 0]
            # Path to save results
            Test_Output = results_dir + "\\" + 'Test Results.csv'
            # save the test plan relevant data to a csv
            test_plan_actual.to_csv(Test_Output, encoding='utf-8', index=False)
            print("Postprocessing complete")
            # record time to downsample analog signals
            t_all = time.time()
            print('Script took %0.3f s' % ((t_all - t0)))


if __name__ == "__main__":

    while True:
        try:
            # take input for raw data directory from automated UBTS
            rootdir = input("Enter automated UBTS data Directory : ")
            exists = os.path.exists(rootdir)
        except:
            print('Invalid path. Please try again')
            # better try again... Return to the start of the loop
            continue
        else:
            if exists:
                # rootdir was successfully parsed
                print('rootdir was successfully parsed')
            elif (rootdir == 'no'):
                rootdir = r"C:\Users\VIERX716\OneDrive - KDP\Documents\Coffee Bloom\20211119_COFFEE_BLOOM"
            else:
                print('Path does not exist. Please try again\n')
                # better try again... Return to the start of the loop
                continue
            break

    main(rootdir)