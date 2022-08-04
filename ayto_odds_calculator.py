# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 14:19:32 2021

@author: Shaun
"""
import pandas as pd
import itertools
from collections import Counter

def ayto_odds(filename=None, nights_df=pd.DataFrame(), truth_booth_df=pd.DataFrame(), suppress_print=True):
    """Given a filename with a 'nights' tab for night matchups and light information
    and a 'booths' tab for truth booth matches and results will output a dataframe
    of possible solutions for each pair and percent of total solutions. Also can
    pass the nights info and truth booth info directly as dataframes"""
    if filename:
        nights_df = pd.read_excel(filename, sheet_name='nights')
        truth_booth_df = pd.read_excel(filename, sheet_name='booths')
    
    all_men = list(nights_df.iloc[:-1,0])
    all_women = list(nights_df.iloc[:-1,1])
    
    men=all_men.copy()
    women=all_women.copy()

    false_truth_booths, true_truth_booths = split_truth_booths(truth_booth_df)
    for match in true_truth_booths:
        women.remove(match[0])
        men.remove(match[1])

    night_data = convert_night_df(nights_df, true_truth_booths)
    unique_combinations = get_solution_space(night_data, women, men, false_truth_booths, suppress_print)

    possibilities_grid = pd.DataFrame(index=all_women, columns=all_men).fillna(0)
    for i in range(len(men)):
        unique_counts = Counter(elem[i] for elem in unique_combinations)
        for woman_count, man_count in unique_counts:
            possibilities_grid.loc[woman_count, man_count] = unique_counts[(woman_count, man_count)]

    for match in true_truth_booths:
        possibilities_grid.loc[match[0], match[1]] = int(len(unique_combinations))

    possibilities_grid.sort_index(inplace=True)
    probability_grid = (possibilities_grid/len(unique_combinations)).round(3)*100
    
    return possibilities_grid, probability_grid, len(unique_combinations)

def split_truth_booths(df):
    """Takes the truth booth dataframe and splits it into perfect matches
    and no matches"""
    false_truth_booths=[]
    true_truth_booths=[]
    for _, truth_booth in df.iterrows():
        if truth_booth['Match?']=='No':
            false_truth_booths.append((truth_booth.Woman, truth_booth.Man))
        elif truth_booth['Match?']=='Yes':
            true_truth_booths.append((truth_booth.Woman, truth_booth.Man))
        else:
            print("Truth Booth tab error")
    return false_truth_booths, true_truth_booths

def convert_night_df(nights_df, true_truth_booths):
    """Takes the dataframe of night information and outputs the following per night:
    [[list of pairs as tuples], number of lights, number of perfect matches present]"""
    night_data=[]
    for name, night in nights_df.iteritems():
        if name=='Men':
            men_night = list(night[:-1])
        else:
            women_night = list(night[:-1])
            match_list = [(women_night[i], men_night[i]) for i in range(len(men_night))]
            perf_matches = len(list(set(true_truth_booths) & set(match_list)))
            night_item =[match_list, int(night[-1:]), perf_matches]
            night_data.append(night_item)
    return night_data

def get_solution_space(night_data, women, men, false_truth_booths, suppress_print=False):
    """Finds all possible solutions given all information available"""
    unique_combinations = []
    count=0
    possible_combinations_checkpoint = factorial(len(men))/4
    permut = itertools.permutations(women, len(men))
    for comb in permut:
        count+=1
        if count >= possible_combinations_checkpoint:
            count=0
            if not suppress_print:
                print('.', end=" ")
        zipped = zip(comb, men)
        solution = list(zipped)
        if not set(solution).isdisjoint(false_truth_booths):
            continue
        valid=True
        for night, lights, perf_matches in night_data:
            if (len(list(set(solution) & set(night))) + perf_matches) != lights: 
                valid=False
                break
        if not valid:
            continue
        unique_combinations.append(solution)
    return unique_combinations

def factorial(n):
    result=1
    for i in range(1,n+1):
        result=result*i
    return result


