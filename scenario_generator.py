from random import randint
from random import choice
import random
import csv
import os
import sys

from numpy import pi

# (1) CONFIG.CSV - INFORMATION
# Defining the parameter estimation modes and
max_depth_set = ['50']
iteration_max_set = ['50']

# (2) SIM.CSV - INFORMATION
# Defining the parameter of simulation file
possible_directions = ['N','S','E','W']
agent_types 		= ['l1','l2','f1','f2']
selected_types 		= [False,False]

def random_pick(set_):
	return set_[randint(0,len(set_)-1)]

def write_config_file(current_folder,parameter_estimation_mode,mcts_mode,train_mode):

	filename = current_folder + 'config.csv'
	with open(filename, 'wb+') as file:
		writer = csv.writer(file, delimiter=',')
		GRID = ['type_selection_mode', 'AS']
		writer.writerows([['type_selection_mode', 'AS']])
		writer.writerows([['parameter_estimation_mode', parameter_estimation_mode]])
		writer.writerows([['train_mode', train_mode]])
		writer.writerows([['generated_data_number', '100']])
		writer.writerows([['reuseTree','False']])
		writer.writerows([['mcts_mode', mcts_mode]])
		writer.writerows([['PF_add_threshold', '0.9']])
		writer.writerows([['PF_del_threshold', '0.9']])
		writer.writerows([['PF_weight', '1.2']])
		writer.writerows([['iteration_max', iteration_max_set[0]]])
		writer.writerows([['max_depth', max_depth_set[0]]])
		writer.writerows([['sim_path', 'sim.csv']])


def generateRandomNumber (grid,gridValue):
	while True:
		testXValue = randint(0, gridValue - 1)
		testYValue = randint(0, gridValue - 1)

		if(grid[testXValue][testYValue] != 1):
			grid[testXValue][testYValue] = 1
			return testXValue,testYValue,grid

def selectType():
	global agent_types, selected_types

	# 1. Selecting a ramdom type
	agentType = choice(agent_types)

	# 2. Verifing if is able to generate this type
	# follower 1 needs lider 1
	if agentType == 'f1' and selected_types[0] == False:
		while agentType != 'l1' or agentType != 'l2':
			agentType = choice(possible_directions)
		if agentType == 'l1':
			selected_types[0] = True
		else:
			selected_types[1] = True
	# follower 2 needs lider 2
	if agentType == 'f2' and selected_types[1] == False:
		while agentType != 'l1' or agentType != 'l2':
			agentType = choice(possible_directions)
		if agentType == 'l1':
			selected_types[0] = True
		else:
			selected_types[1] = True
	# lider 1 and 2 as Selected Type
	if agentType == 'l1':
		selected_types[0] = True
	else:
		selected_types[1] = True

	return agentType

def main():
	# 0. Checking the terminal input
	if len(sys.argv) != 5:
		print 'usage: python scenario_generator.py [experiment] [size] [nagents] [nitems]'
		exit(0)

	# 1. Taking the information
	experiment = argv[1]
	size = int(sys.argv[2])
	nagents = int(sys.argv[3])
	nitems = int(sys.argv[4])

	# 1. Creating the possible configuration files
	# a. choosing the parameter estimation mode
	if experiment == 'MIN':
		train_mode = 'history_based'
	else:
		train_mode = 'none_history_based'

	# b. choosing the mcts mode
	mcts_mode = 'UCTH'
	MC_type = 'O'

	# c. creating the necessary folder
	sub_dir = 'FO_'+ MC_type + '_' + experiment
	current_folder = "inputs/" + sub_dir + '/'
	if not os.path.exists(current_folder):
		os.mkdir(current_folder, 0755)

	# d. creating the config files
	create_config_file(current_folder, experiment, mcts_mode,train_mode)

	# 2. Creating the files
	# a. setting the file name
	filename = current_folder + '/' + 'sim.csv'
	print filename

	# b. creating the a csv file
	with open(filename,'wb+') as file:
		writer = csv.writer(file,delimiter = ',')

		# c. choosing the grid size
		grid_size = size
		grid = [[0 for col in range(grid_size)] for row in range(grid_size)]

		GRID = ['grid',grid_size,grid_size]
		writer.writerows([GRID])

		# d. defining the main agent parameters
		mainx,mainy,grid = generateRandomNumber(grid,grid_size)
		mainDirection    = choice(possible_directions)
		mainType  = 'm'
		mainLevel = 1
		mainRadius, mainAngle = radius, angle

		MAIN = ['main',mainx,mainy,mainDirection,mainType,mainLevel,mainRadius,mainAngle]
		writer.writerows([MAIN])

		# e. defining the commum agents
		nagents = nagents
		for agent_idx in range(nagents):
			agentx,agenty,grid = generateRandomNumber(grid,grid_size)
			agentDirection = choice(possible_directions)
			agentType = selectType()
			agentLevel = round(random.uniform(0,1), 3)
			agentRadius = round(random.uniform(0.1,1), 3)
			agentAngle = round(random.uniform(0.1,1), 3)

			AGENT = ['agent'+ str(agent_idx),agentx,agenty,agentDirection,agentType,agentLevel,agentRadius,agentAngle]
			writer.writerows([AGENT])

		nitems = nitems
		for item_idx in range(nitems):
			itemx,itemy,grid = generateRandomNumber(grid,grid_size)
			itemLevel = round(random.uniform(0,1), 3)

			ITEM = ['item'+ str(item_idx),itemx,itemy,itemLevel]
			writer.writerows([ITEM])

	return current_folder
if __name__ == '__main__':
    main()
