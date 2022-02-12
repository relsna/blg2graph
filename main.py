import sys
import tkinter as tk
from tkinter import filedialog

import blg_to_csv
import csv_to_graph

def options():
	print("""\n 
██████╗ ██╗      ██████╗ ██████╗  ██████╗ ██████╗  █████╗ ██████╗ ██╗  ██╗
██╔══██╗██║     ██╔════╝ ╚════██╗██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██║  ██║
██████╔╝██║     ██║  ███╗ █████╔╝██║  ███╗██████╔╝███████║██████╔╝███████║
██╔══██╗██║     ██║   ██║██╔═══╝ ██║   ██║██╔══██╗██╔══██║██╔═══╝ ██╔══██║
██████╔╝███████╗╚██████╔╝███████╗╚██████╔╝██║  ██║██║  ██║██║     ██║  ██║
╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝  
\nhttps://github.com/relsna/blg2graph""")

	print("""\nOptions:\n
    1. BLG - Create CSV files from a BLG file\n
    2. BLG - Get counters list from a BLG file\n
    3. Graph - Plot a CSV file\n
    0. Exit\n""")


def blg2csv():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilenames()

    relog_output = blg_to_csv.relog(file_path[0])
    timeframe = blg_to_csv.get_timeframe(relog_output)
    date_list = blg_to_csv.date_range(timeframe[0], timeframe[1])
    
    file_list = blg_to_csv.create_daily_csv(file_path[0], date_list)
    print(file_list)


def counterslist():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilenames()

    relog_output = blg_to_csv.relog(file_path[0])
    counter_list = blg_to_csv.get_counters(relog_output)

    print('\n'.join([str(c) for c in counter_list]))

def graph_csv():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilenames()
    print(file_path[0])
    csv_to_graph.graph_all_counters(file_path[0])

while True:
    options()
    option = input("Select an option >>> ")

    if option == "1":
        blg2csv()

    elif option == "2":
        counterslist()

    elif option == "3":
        graph_csv()

    elif option == "0":
        sys.exit()
    else:
        print("Invalid option. Exit? 0")
