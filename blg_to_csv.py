import subprocess
import re
from datetime import datetime, timedelta, time

import tkinter as tk
from tkinter import filedialog

# Takes a Data Collector blg files
#   Create a .csv file per day

#blgname = "C:\\temp\\PerfCounterGraph\\test.blg"

def relog(blg_filename):
    command = ["relog", blg_filename, "-q"]
    res = subprocess.run(command, capture_output=True, text=True)
    return res.stdout


def get_timeframe(relog_output):
    # Return begin and end date from a .blg file (from relog output)
    res = []
    begin_date_index = relog_output.index("Begin:")
    end_date_index =   relog_output.index("End:")

    match = re.search(r'\d{1,2}/\d{1,2}/\d{4}', relog_output[begin_date_index:end_date_index+25])
    begin_date = datetime.strptime(match.group(), '%d/%m/%Y').date()

    match = re.search(r'\d{1,2}/\d{1,2}/\d{4}', relog_output[end_date_index:end_date_index+25])
    end_date = datetime.strptime(match.group(), '%d/%m/%Y').date()

    res.append(begin_date)
    res.append(end_date)
    return res


def get_counters(relog_output):
    # Return a list of counters from a .blg file (relog output)
    # TODO: replace by relog -q (List performance counters in the input file.)
    tmp = relog_output.splitlines()

    counter_list = []
    for i in tmp:
        if "\\\\" in i:
            counter_list.append(i)

    return counter_list


def date_range(start, end):
    # Get all days between Begin and End date
    r = (end+timedelta(days=1)-start).days
    return [start+timedelta(days=i) for i in range(r)]


def create_daily_csv(blg_file, date_list):
    # Takes a .blg files 
    #   Create a .csv file (relog) for every days in date_list

    time_start = time(0,0,1) # 00:00:01
    time_end =   time(23,59,59) # 23:59:59

    file_list = []
    for date in date_list:
        b =  datetime.combine(date, time_start).strftime("%d/%m/%Y %H:%M:%S")
        e =  datetime.combine(date, time_end).strftime("%d/%m/%Y %H:%M:%S")
        file_name = blg_file[:-4] + "_" + str(date) + ".csv"
        file_list.append(file_name)

        command = ["relog", blg_file, "-f", "CSV", "-o", str(file_name), "-b", b, "-e", e, "-y"]

        subprocess.run(command, capture_output=False)
    
    return file_list

def main():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilenames()

    relog_output = relog(file_path[0])
    #print(relog_output)
    timeframe = get_timeframe(relog_output)
    date_list = date_range(timeframe[0], timeframe[1])
    
    #print('\n'.join([str(date) for date in date_list]))
    file_list = create_daily_csv(file_path[0], date_list)
    print('\n'.join([str(f) for f in file_list]))


if __name__ == "__main__":
    main()
