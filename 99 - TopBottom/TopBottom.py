import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
from binance.client import Client
from statistics import mean

# plt.rcParams['figure.figsize'] = [12, 7]
# plt.rc('font', size=14)

def get_data_from_api( pair_symbol, startDate ):
    # -- Define Binance Client --
    client = Client()

    timeInterval = Client.KLINE_INTERVAL_1DAY

    # -- Load all price data from binance API --
    klinesT = client.get_historical_klines(pair_symbol, timeInterval, startDate)

    # -- Define your dataset --
    df = pd.DataFrame(klinesT, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['open'] = pd.to_numeric(df['open'])

    # -- Set the date to index --
    df = df.set_index(df['timestamp'])
    df.index = pd.to_datetime(df.index, unit='ms')
    del df['timestamp']

    # -- Drop all columns we do not need --
    df = df.loc[:,['open', 'high', 'low', 'close']]

    return df

def get_n_columns(df, columns, n):  #n=1
    dt = df.copy()
    for col in columns:
        dt["n"+str(n)+"_"+col] = dt[col].shift(n)
    return dt

def get_top_and_bottom(df, candle_min_window):  #Candle_min_windows = le nbre de chandelle avant et après le top ou le bottom
    originals_columns = list(df.columns.copy())
    originals_columns.append("top")
    originals_columns.append("bottom")
    dt = df.copy()
    dt["bottom"] = 1
    dt["top"] = 1

    for i in range(1, candle_min_window + 1, 1):
        dt = get_n_columns(dt, ['close'], i)
        dt = get_n_columns(dt, ['close'], -i)

        dt.loc[
            (dt["n" + str(-i) + "_close"] < dt["close"]) 
            | (dt["n" + str(i) + "_close"] < dt["close"])
            , "bottom"
        ] = 0

        dt.loc[
            (dt["n" + str(-i) + "_close"] > dt["close"]) 
            | (dt["n" + str(i) + "_close"] > dt["close"])
            , "top"
        ] = 0
#    print(dt)
    dt = dt.loc[:,originals_columns]
    #print(dt)
    return dt

def group_level(df, group_multiplier):  #group_multiplier = 1-> Pas sûr de comprendre cet argument, p-e le nomnre de fois la moyenne
    df_test = df.copy()
    d = list(df_test.loc[df_test["bottom"]==1, "close"])
    d.extend(list(df_test.loc[df_test["top"]==1, "close"]))

    d.sort()

    diff = [y - x for x, y in zip(*[iter(d)] * 2)]  # je devrai comprendre éventuellement cette ligne
    avg = sum(diff) / len(diff)

    important_levels = [[d[0]]]

    for x in d[1:]:
        if x - important_levels[-1][0] < group_multiplier * avg:
            important_levels[-1].append(x)
        else:
            important_levels.append([x])

    return important_levels


def plot_level(pair_symbol, startDate, top_bottom_window, group_multiplier, min_group_number, show_tv_code):
    
    df = get_data_from_api(pair_symbol, startDate)
    df = get_top_and_bottom(df, top_bottom_window)
    levels = group_level(df, group_multiplier)
    
    tv_paste_text = ""

    df["iloc_val"] = list(range(0,len(df),1))
    s = mpf.make_mpf_style(base_mpf_style='charles', rc={'font.size': 6})

    fig1 = mpf.figure(1, figsize=(20, 7), style=s) 
    fig2 = mpf.figure(2, figsize=(20, 7), style=s) 
    ax1 = fig1.add_subplot(111)
    ax2 = fig2.add_subplot(111)


    mpf.plot(df, type='candle', ax=ax1)
    mpf.plot(df, type='candle', ax=ax2)

    plt.figure(1)
    if levels:
        for i in range(len(levels)):
            if len(levels[i]) >= min_group_number:
                plt.hlines(mean(levels[i]), xmin=0, xmax=len(df), colors='blue', lw=len(levels[i]) - (min_group_number - 1))
                tv_paste_text += "\narray.push(levels, " + str(mean(levels[i])) + ")\narray.push(level_width, " + str(len(levels[i]) - (min_group_number - 1)) + ")"

    plt.figure(2)
    for index, row in df.loc[df["top"]==1].iterrows():
        plt.hlines(row["close"],xmin=row["iloc_val"], xmax=len(df), colors='indianred', lw=1)

    for index, row in df.loc[df["bottom"]==1].iterrows():
        plt.hlines(row["close"],xmin=row["iloc_val"], xmax=len(df), colors='purple', lw=1)

    if show_tv_code:
        print(tv_paste_text)
"""
df = get_data_from_api("BTCUSDT", "1 january 2021")
df = get_top_and_bottom(df, 3)
levels = group_level(df, 1)
# df
levels
"""
"""
C'est ci-bas que ça se passe.
"""

plot_level(
    pair_symbol = "THETABTC", 
    startDate = "14 april 2017", 
    top_bottom_window = 3, # le nbre de chandelle avant et après le top ou le bottom
    group_multiplier = 2, # Le nbre de fois que la moyenne est acceptée ### comprendre d'où vient cette moyenne!!!
    min_group_number = 3, # Le nombre de regroupement afficher
    show_tv_code = True
)




