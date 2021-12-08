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
                # collect bloom variables used in this test using log file
                elif (file[-7:-4] == 'log'):
                    parameters = ['Temp:', 'Time:', 'Volume:', 'Size_Selected']
                    # read the log with multiple delimiters
                    with open(UBTS_filename) as fobj:
                        print("\n")
                        print(number)
                        for line in fobj:
                            line_data = re.split('\t|\n|,|[|]', line)
                            if 'V' not in line_data[1]:
                                print(line_data)

if __name__ == "__main__":
    main()
