import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

import json
import base64
from io import BytesIO

json_file = os.path.abspath('config.json')

with open(json_file) as j:    
    json_config = json.load(j)

def get_inclusion_counters(json_config):
    if json_config["matching"]["Apply"]:
        return json_config["matching"]["counters"]
    else:
        return []

def get_exclusion_counters(json_config):
    if json_config["exclude"]["Apply"]:
        return json_config["exclude"]["counters"]
    else:
        return []

def get_timeframe_interval(json_config):
    return json_config["timeframe"]["group_interval"]

def get_timeframe_interval_start_time(json_config):
    return json_config["timeframe"]["start_time"]

def get_timeframe_interval_end_time(json_config):
    return json_config["timeframe"]["end_time"]

# encoded_png = create_graph(col_time, 'line', counter_name, counter_name
#                               , 'r', col_data, [], group_interval)


def create_graph(x, kind, title, l, c, ax1, ax2, group_interval):
    # plotting...
    fig, ax = plt.subplots()

    ax.plot(x, ax1, color=c)
    #ax.plot(x, ax1, color=c, label=l)
    if ax2:
        ax.plot(x, ax2, color=c, label=l)
    
    plt.title(title)

    locator = mdates.AutoDateLocator(minticks=4, maxticks=24)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_ylabel('value')
    ax.set_xlabel(group_interval+' interval')

    #ax.legend(loc="upper left")
    plt.xticks(rotation = 90)
    plt.tight_layout()
    plt.grid()
    #plt.savefig('test_30Min.png')
    my_dpi=120
    #plt.figure(figsize=(800/my_dpi, 800/my_dpi), dpi=my_dpi)

    tmp_file = BytesIO()
    plt.savefig(tmp_file, format='png', dpi=my_dpi)
    encoded_image = base64.b64encode(tmp_file.getvalue()).decode('utf-8')
    plt.close('all')

    return encoded_image


def get_columns_list(csv_file):
    return list(csv_file.columns)


def apply_exclusion_inclusion(columns):

    if get_exclusion_counters(json_config):
        matching_columns = [s for s in columns if any(xs in s for xs in get_exclusion_counters(json_config))]

        # Convert List as Set to remove exclude_counters 
        set_all_columns = set(columns)
        set_matching_columns = set(matching_columns)
        columns_diff = list(set_all_columns - set_matching_columns)

        # Put back the first column (counter collection timestamp) to first item in the list
        #   it's not first anymore after the set transformation...
        columns_diff.insert(0, columns_diff.pop(columns_diff.index(columns[0])))
        columns = columns_diff

    if get_inclusion_counters(json_config):
        include = [s for s in columns if any(xs in s for xs in get_inclusion_counters(json_config))]

        # Put back the first column (counter collection timestamp) to first item in the list
        include.insert(0, columns[0])
        columns = include

    return columns

def graph_all_counters(csv_file):

    print("Starting HTML creation from CSV file...")
    
    perfmon_counters_data = pd.read_csv(csv_file, low_memory=False)
    columns_list = apply_exclusion_inclusion(list(perfmon_counters_data.columns))

    html = "<!DOCTYPE html><html><head><title>" + csv_file + "</title></head><body>"

    for a, c in enumerate(columns_list):
        if a > 0: # exclude first csv column
            print(c)

            cols = [columns_list[0]]
            cols.append(c)
            d = perfmon_counters_data[cols]
            counter_name = str(c).replace("\\", "").replace("/", "_").replace(".", "").replace(":", "").replace(" ", "_")

            for n, c in enumerate(d.columns):
                t = []
                for i, row in enumerate(d.itertuples()):
                    if i > 0:   #remove first line - to replace by slicing ? 
                        if n == 0:
                            t.append(d.loc[i, c])
                        else:
                            if str(d.loc[i, c]).replace('.','',1).isdigit(): # check if float (does not support negative number)
                                t.append(float(d.loc[i, c]))
                            else:
                                t.append(0)
                if n == 0:
                    dff = pd.DataFrame(t)
                    dff.columns = ['col_t']
                else:
                    dff.insert(1, "col_d", t, True)

            dff['col_t'] = pd.to_datetime(dff['col_t'])

            graph_date = str(dff['col_t'][0])[:10]
            start_remove = pd.to_datetime(graph_date + " " + get_timeframe_interval_start_time(json_config))
            end_remove = pd.to_datetime(graph_date + " " + get_timeframe_interval_end_time(json_config))
            dff = dff.query('col_t < @end_remove and col_t > @start_remove')

            group_interval = get_timeframe_interval(json_config)
            print(group_interval)

            dfi = dff.groupby(pd.Grouper(key="col_t",freq=group_interval))['col_d'].mean()

            counter_name = counter_name + "_" + group_interval
            
            col_time = list(dfi.index)
            col_data = [d for d in dfi]

            encoded_png = create_graph(col_time, 'line', counter_name, counter_name, 'r', col_data, [], group_interval)

            html = html + '<img src=\'data:image/png;base64,{}\'>'.format(encoded_png)
    
    html = html + "</body></html>"
    html_file = csv_file[:-4] + ".html"

    with open(html_file, 'w') as f:
        f.write(html)
    
    print(html_file)

def main():
    print("main()...")
    #graph_all_counters(filename)

if __name__ == "__main__":
    main()
