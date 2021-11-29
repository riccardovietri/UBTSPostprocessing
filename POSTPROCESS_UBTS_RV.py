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


def plottemps(results_dir, filename, df):
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
    figure_path = results_dir + '\Plots/PlotTemps_' + filename[-49:] + '.png'
    fig2.savefig(figure_path)  # save the figure to file
    plt.close(fig2)

def plot_UBTS_cases_EN(results_dir, dfs):
    fig, ax = plt.subplots()
    plt.plot(dfs['t268']['Brew Mass (g)_t268']/28.3495, dfs['t268']['T entrance needle (degF)_t268'],
             label='Pulse No Pre-Infusion')
    plt.plot(dfs['t269']['Brew Mass (g)_t269']/28.3495, dfs['t269']['T entrance needle (degF)_t269'],
             label='Pulse 45s Pre-Infusion')
    plt.plot(dfs['t270']['Brew Mass (g)_t270']/28.3495, dfs['t270']['T entrance needle (degF)_t270'],
             label='Pulse 15s Pre-Infusion')
    plt.plot(dfs['t271']['Brew Mass (g)_t271']/28.3495, dfs['t271']['T entrance needle (degF)_t271'],
             label='Europa No Pre-Infusion')
    plt.plot(dfs['t272']['Brew Mass (g)_t272']/28.3495, dfs['t272']['T entrance needle (degF)_t272'],
             label='Europa 45s Pre-Infusion')
    plt.plot(dfs['t273']['Brew Mass (g)_t273']/28.3495, dfs['t273']['T entrance needle (degF)_t273'],
             label='Europa 15s Pre-Infusion')
    ax.legend(loc=0)
    ax.grid()
    ax.set_xlabel("Brew Volume (oz)")
    ax.set_ylabel(r"Entrance Needle Temp (F)")
    plt.title("Entrance Needle Temp vs Brew Volume for all runs")
    plt.xlim([0, 8])
    plt.ylim([190-20, 190+20])
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = results_dir + '/Plots/PlotEntranceNeedleTemps_All_UBTS.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

def plot_UBTS_cases_ES(results_dir, dfs):
    fig, ax = plt.subplots()
    plt.plot(dfs['t268']['Brew Mass (g)_t268']/28.3495, dfs['t268']['T exit stream (degF)_t268'],
             label='Pulse No Pre-Infusion')
    plt.plot(dfs['t269']['Brew Mass (g)_t269']/28.3495, dfs['t269']['T exit stream (degF)_t269'],
             label='Pulse 45s Pre-Infusion')
    plt.plot(dfs['t270']['Brew Mass (g)_t270']/28.3495, dfs['t270']['T exit stream (degF)_t270'],
             label='Pulse 15s Pre-Infusion')
    plt.plot(dfs['t271']['Brew Mass (g)_t271']/28.3495, dfs['t271']['T exit stream (degF)_t271'],
             label='Europa No Pre-Infusion')
    plt.plot(dfs['t272']['Brew Mass (g)_t272']/28.3495, dfs['t272']['T exit stream (degF)_t272'],
             label='Europa 45s Pre-Infusion')
    plt.plot(dfs['t273']['Brew Mass (g)_t273']/28.3495, dfs['t273']['T exit stream (degF)_t273'],
             label='Europa 15s Pre-Infusion')
    ax.legend(loc=0)
    ax.grid()
    ax.set_xlabel("Brew Volume (oz.)")
    ax.set_ylabel(r"Exit Stream Temp (F)")
    plt.title("Exit Stream Temp vs Brew Volume for all runs")
    plt.xlim([0, 8])
    plt.ylim([190-30, 190+10])
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = results_dir + '/Plots/PlotExitStreamTemps_All_UBTS.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

def plot_UBTS_cases_IC(results_dir, dfs):
    fig, ax = plt.subplots()
    plt.plot(dfs['t268']['Brew Mass (g)_t268']/28.3495, dfs['t268']['T in-cup (degF)_t268'],
             label='Pulse No Pre-Infusion')
    plt.plot(dfs['t269']['Brew Mass (g)_t269']/28.3495, dfs['t269']['T in-cup (degF)_t269'],
             label='Pulse 45s Pre-Infusion')
    plt.plot(dfs['t270']['Brew Mass (g)_t270']/28.3495, dfs['t270']['T in-cup (degF)_t270'],
             label='Pulse 15s Pre-Infusion')
    plt.plot(dfs['t271']['Brew Mass (g)_t271']/28.3495, dfs['t271']['T in-cup (degF)_t271'],
             label='Europa No Pre-Infusion')
    plt.plot(dfs['t272']['Brew Mass (g)_t272']/28.3495, dfs['t272']['T in-cup (degF)_t272'],
             label='Europa 45s Pre-Infusion')
    plt.plot(dfs['t273']['Brew Mass (g)_t273']/28.3495, dfs['t273']['T in-cup (degF)_t273'],
             label='Europa 15s Pre-Infusion')
    ax.legend(loc=0)
    ax.grid()
    ax.set_xlabel("Brew Volume (oz.)")
    ax.set_ylabel(r"In Cup  Temp (F)")
    plt.title("In Cup Temp vs Brew Volume for all runs")
    plt.xlim([0, 8])
    plt.ylim([140, 190])
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = results_dir + '/Plots/PlotInCupTemps_All_UBTS.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Main program function
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def main():
    # Begin timing how long the script takes
    t0 = time.time()
    rootdir = r"C:\Users\VIERX716\OneDrive - KDP\Documents\Coffee Bloom\UBTS005\TEMP_PROFILES"
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
    drip_vols = [0] * file_count
    brew_size = [0] * file_count
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

                    df, notes = import_UBTS(UBTS_filename)
                    if "PULSE" in notes:
                        brew_code[i] = ['Pulse']
                    else:
                        brew_code[i] = ['Europa']

                    if df['Sample Time (s)'].iloc[-1] == 'Sample Time (s)':
                        print('Dropping last row for file: ' + file)
                        df.drop(df.tail(1).index, inplace=True)  # drop last row
                    dfs['t' + str(tests[i])] = df.shift(i).add_suffix('_t' + str(tests[i]))

                    #plottemps(results_dir, UBTS_filename, df)

                    Test_UBTS_Data = results_dir + "\\" + str(tests[i]) + ' Data.csv'

                    df.to_csv(Test_UBTS_Data, encoding='utf-8', index=False)

                # collect bloom variables used in this test using log file
                elif file[-7:-4] == 'log':
                    parameters = ['Temp:', 'Time:', 'Volume:', 'Size_Selected']
                    # read the log with multiple delimiters
                    with open(UBTS_filename) as fobj:
                        js.append(i)
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

                else:
                    js.append(i)

    for j in sorted(js, reverse=True):
        del tests[j]
        del brew_code[j]
        del brew_size[j]
        del drip_vols[j]
        del bloom_temps[j]
        del bloom_vols[j]
        del bloom_times[j]

    d = {'Test Number': tests,
         'Brew Code': brew_code,
         'Brew Size': brew_size,
         'Drip Vol (mL)': drip_vols,
         'Bloom Temp (F)': bloom_temps,
         'Bloom Time (s)': bloom_times,
         'Bloom Volume (ml)': bloom_vols,
         }
    df = pd.DataFrame(data=d)

    Brew_Stats = rootdir + "\\" + 'Results' + "\\" + 'Brew Stats.csv'
    df.to_csv(Brew_Stats, encoding='utf-8', index=False)

    # plot all UBTS Cases
    #plot_UBTS_cases_EN(results_dir, dfs)
    #plot_UBTS_cases_ES(results_dir, dfs)
    #plot_UBTS_cases_IC(results_dir, dfs)

    fig, ax = plt.subplots()
    plt.plot(dfs['t268']['Brew Mass (g)_t268']/28.3495, dfs['t268']['T in-cup (degF)_t268'],
             label='Pulse No Pre-Infusion')
    plt.plot(dfs['t271']['Brew Mass (g)_t271']/28.3495, dfs['t271']['T in-cup (degF)_t271'],
             label='Europa No Pre-Infusion')
    ax.legend(loc=0)
    ax.grid()
    ax.set_xlabel("Brew Volume (oz.)")
    ax.set_ylabel(r"In Cup  Temp (F)")
    plt.title("In Cup Temp vs Brew Volume")
    plt.xlim([0, 8])
    plt.ylim([80, 190])
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = results_dir + '/Plots/PlotInCupTemps_Base_UBTS.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

    fig, ax = plt.subplots()
    plt.plot(dfs['t268']['Brew Mass (g)_t268'] / 28.3495, dfs['t268']['T in-cup (degF)_t268'],
             label='Pulse No Pre-Infusion')
    plt.plot(dfs['t271']['Brew Mass (g)_t271'] / 28.3495, dfs['t271']['T in-cup (degF)_t271'],
             label='Europa No Pre-Infusion')
    ax.legend(loc=0)
    ax.grid()
    ax.set_xlabel("Brew Volume (oz.)")
    ax.set_ylabel(r"In Cup  Temp (F)")
    plt.title("In Cup Temp vs Brew Volume")
    plt.xlim([0, 8])
    plt.ylim([80, 190])
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = results_dir + '/Plots/PlotInCupTemps_Base_UBTS.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

    fig, ax = plt.subplots()
    plt.plot(dfs['t269']['Brew Mass (g)_t269'] / 28.3495, dfs['t269']['T in-cup (degF)_t269'], 'g',
             label='Pulse 45s Pre-Infusion')
    plt.plot(dfs['t272']['Brew Mass (g)_t272'] / 28.3495, dfs['t272']['T in-cup (degF)_t272'], 'm',
             label='Europa 45s Pre-Infusion')
    ax.legend(loc=0)
    ax.grid()
    ax.set_xlabel("Brew Volume (oz.)")
    ax.set_ylabel(r"In Cup  Temp (F)")
    plt.title("In Cup Temp vs Brew Volume")
    plt.xlim([0, 8])
    plt.ylim([140, 190])
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = results_dir + '/Plots/PlotInCupTemps_45s_UBTS.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

    fig, ax = plt.subplots()
    plt.plot(dfs['t269']['Brew Mass (g)_t269'], dfs['t269']['T entrance needle (degF)_t269'], 'g',
             label='Pulse 45s 90c Pre-Infusion')
    plt.plot(dfs['t272']['Brew Mass (g)_t272'], dfs['t272']['T entrance needle (degF)_t272'], 'm',
             label='Europa 45s 90c Pre-Infusion')
    ax.legend(loc=0)
    ax.grid()
    ax.set_xlabel("Brew Mass (g)")
    ax.set_ylabel(r"Entrance Needle Temp (F)")
    plt.title("Entrance Needle Temp vs Brew Volume")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = results_dir + '/Plots/PlotENTemps_45s_UBTS.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

    fig, ax = plt.subplots()
    plt.plot(dfs['t270']['Brew Mass (g)_t270'], dfs['t270']['T entrance needle (degF)_t270'], 'g',
             label='Pulse 15s 90c Pre-Infusion')
    plt.plot(dfs['t273']['Brew Mass (g)_t273'], dfs['t273']['T entrance needle (degF)_t273'], 'm',
             label='Europa 15s 90c Pre-Infusion')
    ax.legend(loc=0)
    ax.grid()
    ax.set_xlabel("Brew Mass (g)")
    ax.set_ylabel(r"Entrance Needle Temp (F)")
    plt.title("Entrance Needle Temp vs Brew Volume")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = results_dir + '/Plots/PlotENTemps_15s_UBTS.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

    fig, ax = plt.subplots()
    plt.plot(dfs['t271']['Brew Mass (g)_t271'], dfs['t271']['T entrance needle (degF)_t271'],
             label='Europa No Pre-Infusion')
    plt.plot(dfs['t272']['Brew Mass (g)_t272'] , dfs['t272']['T entrance needle (degF)_t272'], 'm',
             label='Europa 45s 90c Pre-Infusion')
    plt.plot(dfs['t273']['Brew Mass (g)_t273'], dfs['t273']['T entrance needle (degF)_t273'], 'r',
             label='Europa 15s 90c Pre-Infusion')
    ax.legend(loc=0)
    ax.grid()
    ax.set_xlabel("Brew Mass (g)")
    ax.set_ylabel(r"Entrance Needle Temp (F)")
    plt.title("Entrance Needle Temp vs Brew Volume")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = results_dir + '/Plots/PlotENTemps_Europa_UBTS.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

    fig, ax = plt.subplots()
    plt.plot(dfs['t271']['Brew Mass (g)_t271'], dfs['t271']['T entrance needle (degF)_t271'],
             label='Europa No Pre-Infusion')
    plt.plot(dfs['t272']['Brew Mass (g)_t272'], dfs['t272']['T entrance needle (degF)_t272'], 'm',
             label='Europa 45s 90c Pre-Infusion')
    plt.plot(dfs['t273']['Brew Mass (g)_t273'], dfs['t273']['T entrance needle (degF)_t273'], 'r',
             label='Europa 15s 90c Pre-Infusion')
    ax.legend(loc=0)
    ax.grid()
    plt.xlim([0, 50])
    ax.set_xlabel("Brew Mass (g)")
    ax.set_ylabel(r"Entrance Needle Temp (F)")
    plt.title("Entrance Needle Temp vs Brew Volume")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = results_dir + '/Plots/PlotENTemps_Europa_UBTS_zoomed.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)


    fig, ax = plt.subplots()
    plt.plot(dfs['t274']['Sample Time (s)_t274'], dfs['t274']['T entrance needle (degF)_t274'],
             label='20 s 17 ml 80 c run 0')
    plt.plot(dfs['t275']['Sample Time (s)_t275'], dfs['t275']['T entrance needle (degF)_t275'],
             label='20 s 17 ml 80 c run 1')
    plt.plot(dfs['t276']['Sample Time (s)_t276'], dfs['t276']['T entrance needle (degF)_t276'],
             label='20 s 17 ml 80 c run 2')
    ax.legend(loc=0)
    ax.grid()
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(r"Entrance Needle Temp (F)")
    plt.title("Entrance Needle Temp vs Time")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = results_dir + '/Plots/PlotEntranceTemps_274-276UBTS.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

    fig, ax = plt.subplots()
    plt.plot(dfs['t277']['Sample Time (s)_t277'], dfs['t277']['T entrance needle (degF)_t277'],
             label='20 s 17 ml 85 c run 0')
    plt.plot(dfs['t278']['Sample Time (s)_t278'], dfs['t278']['T entrance needle (degF)_t278'],
             label='20 s 17 ml 85 c run 1')
    plt.plot(dfs['t279']['Sample Time (s)_t279'], dfs['t279']['T entrance needle (degF)_t279'],
             label='20 s 17 ml 85 c run 2')
    ax.legend(loc=0)
    ax.grid()
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(r"Entrance Needle Temp (F)")
    plt.title("Entrance Needle Temp vs Time")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = results_dir + '/Plots/PlotEntranceTemps_277-279UBTS.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

    fig, ax = plt.subplots()
    plt.plot(dfs['t280']['Sample Time (s)_t280'], dfs['t280']['T entrance needle (degF)_t280'],
             label='20 s 17 ml 90 c run 0')
    plt.plot(dfs['t281']['Sample Time (s)_t281'], dfs['t281']['T entrance needle (degF)_t281'],
             label='20 s 17 ml 90 c run 1')
    plt.plot(dfs['t282']['Sample Time (s)_t282'], dfs['t282']['T entrance needle (degF)_t282'],
             label='20 s 17 ml 90 c run 2')
    ax.legend(loc=0)
    ax.grid()
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(r"Entrance Needle Temp (F)")
    plt.title("Entrance Needle Temp vs Time")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = results_dir + '/Plots/PlotEntranceTemps_280-282UBTS.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

    t1 = 't296'
    t2 = 't297'
    t3 = 't298'
    fig, ax = plt.subplots()
    plt.plot(dfs[t1]['Sample Time (s)_' + t1], dfs[t1]['T entrance needle (degF)_' + t1],
             label='14ml 20s 90c First Run')
    plt.plot(dfs[t2]['Sample Time (s)_' + t2], dfs[t2]['T entrance needle (degF)_' + t2],
             label='14ml 20s 90c Second Run')
    plt.plot(dfs[t3]['Sample Time (s)_' + t3], dfs[t3]['T entrance needle (degF)_' + t3],
             label='14ml 20s 90c Third Run')
    ax.legend(loc=0)
    ax.grid()
    plt.xlim([0, 50])
    ax.set_xlabel("Sample Time (s)")
    ax.set_ylabel(r"Entrance Needle Temp (F)")
    plt.title("Entrance Needle Temp vs Time")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = drip_dir + '/PlotENTemps_296-298_UBTS_zoomed.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

    fig, ax = plt.subplots()
    plt.plot(dfs[t1]['Brew Mass (g)_' + t1], dfs[t1]['T entrance needle (degF)_' + t1],
             label='14ml 20s 90c First Run')
    plt.plot(dfs[t2]['Brew Mass (g)_' + t2], dfs[t2]['T entrance needle (degF)_' + t2],
             label='14ml 20s 90c Second Run')
    plt.plot(dfs[t3]['Brew Mass (g)_' + t3], dfs[t3]['T entrance needle (degF)_' + t3],
             label='14ml 20s 90c Third Run')
    ax.legend(loc=0)
    ax.grid()
    plt.xlim([0, 30])
    ax.set_xlabel("Brew Mass (g)")
    ax.set_ylabel(r"Entrance Needle Temp (F)")
    plt.title("Entrance Needle Temp vs Brew Mass")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = drip_dir + '/PlotENTemps_296-298vsMass_UBTS_zoomed.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

    t0 = 't290'
    t1 = 't293'
    t2 = 't294'
    t3 = 't295'
    fig, ax = plt.subplots()
    plt.plot(dfs[t0]['Sample Time (s)_' + t0], dfs[t0]['T entrance needle (degF)_' + t0],
             label='15ml 20s 90c First Run - no Rinse')
    plt.plot(dfs[t1]['Sample Time (s)_' + t1], dfs[t1]['T entrance needle (degF)_' + t1],
             label='15ml 20s 90c First Run')
    plt.plot(dfs[t2]['Sample Time (s)_' + t2], dfs[t2]['T entrance needle (degF)_' + t2],
             label='15ml 20s 90c Second Run')
    plt.plot(dfs[t3]['Sample Time (s)_' + t3], dfs[t3]['T entrance needle (degF)_' + t3],
             label='15ml 20s 90c Third Run')
    ax.legend(loc=0)
    ax.grid()
    plt.xlim([0, 50])
    ax.set_xlabel("Sample Time (s)")
    ax.set_ylabel(r"Entrance Needle Temp (F)")
    plt.title("Entrance Needle Temp vs Time")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = drip_dir + '/PlotENTemps_293-295_UBTS_zoomed.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

    fig, ax = plt.subplots()
    plt.plot(dfs[t0]['Brew Mass (g)_' + t0], dfs[t0]['T entrance needle (degF)_' + t0],
             label='15ml 20s 90c First Run - no Rinse')
    plt.plot(dfs[t1]['Brew Mass (g)_' + t1], dfs[t1]['T entrance needle (degF)_' + t1],
             label='15ml 20s 90c First Run')
    plt.plot(dfs[t2]['Brew Mass (g)_' + t2], dfs[t2]['T entrance needle (degF)_' + t2],
             label='15ml 20s 90c Second Run')
    plt.plot(dfs[t3]['Brew Mass (g)_' + t3], dfs[t3]['T entrance needle (degF)_' + t3],
             label='15ml 20s 90c Third Run')
    ax.legend(loc=0)
    ax.grid()
    plt.xlim([0, 30])
    ax.set_xlabel("Brew Mass (g)")
    ax.set_ylabel(r"Entrance Needle Temp (F)")
    plt.title("Entrance Needle Temp vs Brew Mass")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = drip_dir + '/PlotENTemps_293-295vsMass_UBTS_zoomed.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)

    t1 = 't280'
    t2 = 't281'
    t3 = 't282'
    fig, ax = plt.subplots()
    plt.plot(dfs[t1]['Sample Time (s)_' + t1], dfs[t1]['T entrance needle (degF)_' + t1],
             label='17ml 20s 90c First Run')
    plt.plot(dfs[t2]['Sample Time (s)_' + t2], dfs[t2]['T entrance needle (degF)_' + t2],
             label='17ml 20s 90c Second Run')
    plt.plot(dfs[t3]['Sample Time (s)_' + t3], dfs[t3]['T entrance needle (degF)_' + t3],
             label='17ml 20s 90c Third Run')
    ax.legend(loc=0)
    ax.grid()
    plt.xlim([0, 50])
    ax.set_xlabel("Sample Time (s)")
    ax.set_ylabel(r"Entrance Needle Temp (F)")
    plt.title("Entrance Needle Temp vs Time")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    figure_path = drip_dir + '/PlotENTemps_280-282_UBTS_zoomed.png'
    fig.savefig(figure_path)  # save the figure to file
    plt.close(fig)


if __name__ == "__main__":
    main()
