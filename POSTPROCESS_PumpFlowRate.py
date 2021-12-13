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
    rootdir = r"C:\Users\VIERX716\OneDrive - KDP\Documents\Coffee Bloom\DOE v4\Test"
    # Results Directory
    results_dir = os.path.join(rootdir, 'Results')
    # Plots Directory
    plots_dir = os.path.join(results_dir, 'Plots')

    # Create a Results folder to save images and the files
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print('\nCreating Results Folder: \n')
    else:
        print('\nResults Folder: \n')
    print(results_dir)
    # Also create plots directory
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)


    # step through data directory looking for UBTS files
    for subdir, dirs, files in os.walk(rootdir):
        if not ((subdir == results_dir) or (subdir == plots_dir)):
            for i in range(len(files)):
                file = files[i]
                filename = rootdir + '\\' + file
                if (file[-4:] == '.log'):
                    # if file was log file from teraterm log, create mass arrays froms cale
                    mass = []
                    m_time = []
                    with open(filename) as fobj:
                        # initialize the time of mass reading as zero
                        prev_time = 0
                        for line in fobj:
                            line_data = re.split('\t|\n|,| |]', line)
                            for j in range(len(line_data)):
                                # The only float numbers in the log data are the masses
                                # when mass is found in one line, collect the time and mass
                                if (is_float(line_data[j])):
                                    prev_time = prev_time + (float(line_data[1][-6:]) - prev_time)
                                    m_time.append(prev_time)
                                    mass.append(float(line_data[j]))
                    # After reading through the log file, create a dataframe
                    df_scale = pd.DataFrame({'Time': m_time, 'Mass': mass})
                    z_scores = stats.zscore(df_scale)

                    abs_z_scores = np.abs(z_scores)
                    filtered_entries = (abs_z_scores < 3).all(axis=1)
                    new_df_scale = df_scale[filtered_entries]
                    df_scale['Smooth_Mass'] = df_scale.Mass.rolling(8).mean()

                elif ("Test" in file) and (file[-4:] == '.lvm'):
                    df = pd.read_csv(filename, sep='\t', skiprows=23, header=0)
                    size_df = len(df.X_Value)
                    times_NI = np.linspace(0, (1/3)*size_df, size_df)
                    df['Time'] = times_NI

            non_zero_voltages = df[(df.Voltage > 0.1)]
            voltage_time = non_zero_voltages.Time.iloc[-1]-non_zero_voltages.Time.iloc[0]
            voltage = non_zero_voltages.Voltage.mean()
            non_zero_mass = df_scale[(df_scale.Smooth_Mass > 0.1)]
            mass_time = non_zero_mass.Time.iloc[-1] - non_zero_mass.Time.iloc[0]
            mass_change = non_zero_mass.Mass.iloc[-1] - non_zero_mass.Mass.iloc[0]
            print("Change in Mass")
            print(mass_change)
            print("Time change in Mass")
            print(mass_time)
            print("Voltage")
            print(voltage)
            print("Time change in voltage")
            print(voltage_time)

            fig, ax = plt.subplots()
            color = 'tab:red'
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Voltage', color=color)
            ax.plot(df.Time, df.Voltage, label='Voltage', color=color)
            ax.tick_params(axis='y', labelcolor=color)

            ax2 = ax.twinx()
            color = 'tab:blue'
            ax2.set_ylabel('Mass', color=color)  # we already handled the x-label with ax
            ax2.tick_params(axis='y', labelcolor=color)
            ax2.plot(new_df_scale.Time, new_df_scale.Mass,  label='Mass', color=color)
            ax2.plot(df_scale.Time, df_scale.Smooth_Mass,  label='Mass_smooth', color='green')
            ax2.legend(loc=0)
            ax2.grid()
            plt.title("Temp vs Brew Mass " + filename[-12:-4])
            fig.tight_layout()  # otherwise the right y-label is slightly clipped
            figure_path = plots_dir + '\Test1.png'
            fig.savefig(figure_path)  # save the figure to file
            plt.close(fig)

if __name__ == "__main__":
    main()
