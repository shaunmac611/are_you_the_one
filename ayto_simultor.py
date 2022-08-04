# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 21:45:14 2021

@author: Shaun
"""
from ayto_game_generator import AYTO
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

def run_game():
    results  = pd.DataFrame(columns=[i/2 for i in range(1, 40+1)])

    for i in range(90):
        start=time.time()
        men = ['man' + str(i) for i in range(1,11)]
        women = ['woman' + str(i) for i in range(1,11)]
        ayto=AYTO(men, women, generated=True)
        ayto.simulate_game()
        game_tracker = unzip(ayto.game_tracker)
        result = game_tracker[1]
        result.extend([np.nan for i in range(len(results.columns) - len(game_tracker[1]))])
        results.loc[len(results)] = result
        print(str(round((time.time() - start)/60,2)), end=' | ')
    plot_results(results)
    histogram_results(results)
    
def unzip(tuple_list):
    return [[ i for i, j in tuple_list ],
            [ j for i, j in tuple_list ]]

def plot_results(results):
    ten_factorial = 3_628_800
    plot_results=results.copy()
    plot_results.insert(loc=0, column=0, value=ten_factorial)
    median_path = find_median_path(plot_results)
    
    for i in range(len(results.index)):
        plot_item = plot_results.loc[i,:].copy()
        plot_item.iloc[list(plot_item).index(1)+1:]=np.nan
        plt.plot(plot_item, color='Gainsboro')
        plt.yscale("log")
    
    plot_results_stats = [(median_path,'median', 'DarkSlateGray', '--'),
                          (plot_results.min(),'min', 'blue', '-'),
                          (plot_results.max(),'max', 'red', '-')]
    
    for metric, label, color, dash_type in plot_results_stats:
        metric.iloc[list(metric).index(1)+1:]=np.nan
        plt.plot(metric, dash_type, color=color, label=label)
        plt.yscale("log")
    plt.legend() 
    plt.ylabel('Possible Solutions')
    plt.xlabel('Week')
    plt.title('Are You The One Simulations')
    plt.savefig('ayto_2.png', dpi=300)
    plt.close()

def histogram_results(results):
    df = results.copy()
    df['len_play'] = (df.count(axis=1)-1)/2
    df['len_win'] = (df[df!=1].count(axis=1)+1)/2

    col = 'len_win'
    plt.hist(df[col], bins=[4.25 + i*.5 for i in range(16)], rwidth=.7, weights=np.ones(len(df[col])) / len(df[col]))
    plt.title("Night where a win is guaranteed")
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.savefig('ayto_histogram_4.png', dpi=300)
    
def find_median_path(plot_results):
    df = plot_results.copy()
    df['len'] = df.count(axis=1)
    df = df[df['len']==df['len'].median()]
    
    col=-3
    while len(df)>1:
        col_label = df.dropna(axis=1).iloc[:,col].name
        df_med = df.loc[df[col_label] == round(df.dropna(axis=1).iloc[:,col].median()), col_label].iloc[0]
        df = df[df[col_label]==df_med]
        col = col - 1
    return df.iloc[:,:-1].squeeze()

def find_mean_path(results):
    df = results.copy()
    df['len'] = plot_results.count(axis=1)
    df = df[df['len']==df['len'].mean()]
    
    col=-3
    while len(df)>1:
        col_label = df.dropna(axis=1).iloc[:,col].name
        df_mean = df.loc[df[col_label] == round(df.dropna(axis=1).iloc[:,col].mean()), col_label].iloc[0]
        df = df[df[col_label]==df_mean]
        col = col - 1
    return df.iloc[:,:-1].squeeze()
    