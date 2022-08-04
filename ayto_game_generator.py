# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 15:14:24 2021

@author: Shaun
"""
import random 
import pandas as pd
import itertools
from collections import Counter

class AYTO:

    def __init__(self, men, women_init, generated=False):
        if generated:
            self.women = women_init.copy()
            random.shuffle(self.women)
            self.solution = [(self.women[i], men[i]) for i in range(0, len(men))]
        else:
            self.women = women_init.copy()
        self.men, self.in_house_men = men, men
        self.women, self.in_house_women  = self.women, self.women
        self.night_data = []
        self.perfect_matches, self.no_matches = [], []
        self.init_solution_space()
        self.update_results_matrices()
        self.week = 0
        self.game_tracker = []
        
    def add_truth_booth(self, person_1, person_2, match_status=None):
        if person_1 in self.men and person_2 in self.women:
            man=person_1
            woman=person_2
            valid=True
        elif person_1 in self.women and person_2 in self.men:
            man=person_2
            woman=person_1
            valid=True
        else:
            print("Truth Booth Participants not recognized")
            valid=False
        if valid:
            self.week = self.week + 0.5
            if match_status is None:
                if len(list(set([(woman, man)]) & set(self.solution))) == 1:
                    match_status=True
                else:
                    match_status=False
            if match_status==True or match_status=='Yes':
                self.perfect_matches.append((woman, man))
            elif match_status==False or match_status =='No':
                self.no_matches.append((woman, man))

    def add_night_data(self, couples, lights):
        self.night_data.append([couples, lights, self.perfect_match_count(couples)])
        self.week = self.week+0.5
    
    def update_night_data(self):
        temp_night_data=[]
        for couples, lights, _ in self.night_data:
            temp_night_data.append([couples, lights, self.perfect_match_count(couples)])
        self.night_data = temp_night_data
    
    def perfect_match_count(self, couples):
        return len(list(set(couples) & set(self.perfect_matches)))
    
    def light_count(self, couples):
        return len(list(set(couples) & set(self.solution)))
    
    def play_a_night(self, couples):
        self.add_night_data(couples, self.light_count(couples))
    
    def update_in_house(self):
        for match in self.perfect_matches:
            if match[0] in self.in_house_women:
                self.in_house_women.remove(match[0])
            elif match[1] in self.in_house_women:
                self.in_house_women.remove(match[1])
                
            if match[0] in self.in_house_men:
                self.in_house_men.remove(match[0])
            elif match[1] in self.in_house_men:
                self.in_house_men.remove(match[1])
                
    def get_solution_space(self, suppress_print=False):
        """Finds all possible solutions given all information available"""
        self.update_in_house()
        self.update_night_data()
        self.unique_combinations = []
        count=0
        possible_combinations_checkpoint = self.factorial(len(self.men))/4
        permut = itertools.permutations(self.in_house_women, len(self.in_house_men))
        for comb in permut:
            count+=1
            if count >= possible_combinations_checkpoint:
                count=0
                if not suppress_print:
                    print('.', end=" ")
            zipped = zip(comb, self.in_house_men)
            possible_solution = list(zipped)
            if not set(possible_solution).isdisjoint(self.no_matches):
                continue
            valid=True
            for night, lights, perf_matches in self.night_data:
                if (len(list(set(possible_solution) & set(night))) + perf_matches) != lights: 
                    valid=False
                    break
            if not valid:
                continue
            self.unique_combinations.append(possible_solution)
        self.game_tracker.append([self.week, len(self.unique_combinations)])
    
    def init_solution_space(self):
        """Finds all possible solutions given all information available"""
        self.unique_combinations = []
        permut = itertools.permutations(self.in_house_women, len(self.in_house_men))
        for comb in permut:
            zipped = zip(comb, self.in_house_men)
            possible_solution = list(zipped)
            self.unique_combinations.append(possible_solution)
            
    def update_results_matrices(self):
        self.possibilities_grid = pd.DataFrame(index=self.women, columns=self.men).fillna(0)
        for i in range(len(self.in_house_men)):
            unique_counts = Counter(elem[i] for elem in self.unique_combinations)
            for woman_count, man_count in unique_counts:
                self.possibilities_grid.loc[woman_count, man_count] = unique_counts[(woman_count, man_count)]
        for match in self.perfect_matches:
            self.possibilities_grid.loc[match[0], match[1]] = int(len(self.unique_combinations))
        self.possibilities_grid.sort_index(inplace=True)
        self.probability_grid = (self.possibilities_grid/len(self.unique_combinations)).round(3)*100
        
    def implicit_perfect_matches(self):
        for man in self.probability_grid.columns:
            if len(self.probability_grid[self.probability_grid[man]==100])>0:
                woman = self.probability_grid[self.probability_grid[man]==100].index.values[0]
                perf_match = (woman,man)
                if perf_match not in self.perfect_matches:
                    self.perfect_matches.append((woman, man))
    
    def factorial(self, n):
        result=1
        for i in range(1,n+1):
            result=result*i
        return result
    
    def random_night_guess(self):
        self.update_in_house()
        women_guess = self.in_house_women.copy()
        random.shuffle(women_guess)
        if len(self.unique_combinations) == 0:
            couples = list(zip(women_guess, self.in_house_men))
        else:
            couples = random.choice(self.unique_combinations)
        if len(self.perfect_matches)>0:
            couples.extend(self.perfect_matches)
        return couples

    def get_best_truth_booth_couple(self):
        temp_probability_grib = self.probability_grid.copy()
        temp_probability_grib = temp_probability_grib-50
        temp_probability_grib = temp_probability_grib.abs()
        man_min = temp_probability_grib.min().idxmin()
        woman_min = temp_probability_grib[man_min].idxmin()
        return woman_min, man_min

    def random_day_n(self):
        self.implicit_perfect_matches()
        self.update_results_matrices()
        woman_min, man_min = self.get_best_truth_booth_couple()
        self.add_truth_booth(woman_min, man_min)
        self.get_solution_space(suppress_print=True)
        
        self.implicit_perfect_matches()
        self.update_results_matrices()
        couples = self.random_night_guess()
        self.play_a_night(couples)
        self.get_solution_space(suppress_print=True)

    def simulate_game(self):
        while len(self.unique_combinations) > 1:
            self.random_day_n()
