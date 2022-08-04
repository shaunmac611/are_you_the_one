# are_you_the_one
are you the one simulator and solver
Solver:
ayto_odds_calculator.py
Takes in an excel file with a nights tab anda  booths tab, the nights tab has the pairings for each nights and the number of lights assoicated with that pairing
The booths tab has the couples sent to the turth booth and whether or not they are a match
sample_input.xlsx is the necessary format for file input, the Group headers (Group 1 and Group 2) are necesssary and must align accross tabs

Simulator:
ayto_game_generator.py creates a fake game and takes two lists of the same length of people as input, the lists will be used to generate a pairing (example in season 1 the lists would be: the name of the men, and seperately the name of the women). Object is capable of adding booth information, adding night information, and will update probabilities based on ayto_odd_calculator.
ayto_simulator.py will create several AYTO objects and 'solve' them by putting in random nights (but only ever putting in nights that are in the possible solution space, but not optimized) but will put in optimizied truth booths (specifically the pairing that is cloest to 50% and will therefore elminiate the most possibilities)

