import random
import simulator.simulator.simulator

import numpy as np
from sklearn import linear_model

actions = ['up', 'down', 'right', 'left', 'load']
types = ['l1', 'l2', 'f1', 'f2']

radius_max = 1
radius_min = -1
angle_max = 1
angle_min = -1
level_max = 1
level_min = 0

# P(teta|H)
p_type_l1 = []
p_type_l2 = []
p_type_f1 = []
p_type_f2 = []

# P(a|H,teta,p)
p_action_parameter_type_l1 = []
p_action_parameter_type_l2 = []
p_action_parameter_type_f1 = []
p_action_parameter_type_f2 = []

parameters_values_l1 = []
parameters_values_l2 = []
parameters_values_f1 = []
parameters_values_f2 = []


def select_subset_types():
    return types[0]


def if_markovian(pt):
    return False


def initialisation():
    # P(teta|H)
    p_type_l1.append(round(random.uniform(0, 1), 1))
    p_type_l2.append(round(random.uniform(0, 1), 1))
    p_type_f1.append(round(random.uniform(0, 1), 1))
    p_type_f2.append(round(random.uniform(0, 1), 1))

    # parameters estimated values for each type
    parameters_values_l1.append(create_random_parameters())
    parameters_values_l2.append(create_random_parameters())
    parameters_values_f1.append(create_random_parameters())
    parameters_values_f2.append(create_random_parameters())


def create_random_parameters():
    tmp_parameter = []
    tmp_parameter.append(round(random.uniform(radius_min, radius_max), 2))  # 'radius'
    tmp_parameter.append(round(random.uniform(angle_min, angle_max), 2))  # 'angle'
    tmp_parameter.append(round(random.uniform(level_min, level_max), 2))  # 'level'
    return tmp_parameter


def update_belief(time_step, agent_type):
    # get the value of p in t-1
    if agent_type == 'l1':
        p_type_l1.append(p_type_l1[time_step - 1] * p_action_parameter_type_l1[time_step - 1])

    if agent_type == 'l2':
        p_type_l2.append(p_type_l2[time_step - 1] * p_action_parameter_type_l2[time_step - 1])

    if agent_type == 'f1':
        p_type_f1.append(p_type_f1[time_step - 1] * p_action_parameter_type_f1[time_step - 1])

    if agent_type == 'f2':
        p_type_f2.append(p_type_f2[time_step - 1] * p_action_parameter_type_f2[time_step - 1])


def update_parameter_estimate(time_step, agent_type):
    data_numbers = 10
    # Generating  D = (p,f(p)) , f(p) = P(a|H_t_1,teta,p)
    D = generate_data_for_update_parameter(agent_type, data_numbers)

    x_train = []
    y_train = []
    for i in range(0, data_numbers):
        x_train.append(D[i][0:3])
        y_train.append(D[i][3])

        # get the value of p in t-1
    if agent_type == 'l1':
        old_parameters_estimation = parameters_values_l1[time_step - 1]

    if agent_type == 'l2':
        old_parameters_estimation = parameters_values_l2[time_step - 1]

    if agent_type == 'f1':
        old_parameters_estimation = parameters_values_f1[time_step - 1]

    if agent_type == 'f2':
        old_parameters_estimation = parameters_values_f2[time_step - 1]

    # parameters value order is : radius , angle, level
    new_parameters_estimation = calculate_gradient_ascent(time_step, x_train, y_train,
                                                          old_parameters_estimation)  # D = (p,f(p)) , f(p) = P(a|H_t_1,teta,p)

    if agent_type == 'l1':
        parameters_values_l1.append(new_parameters_estimation)

    if agent_type == 'l2':
        parameters_values_l2.append(new_parameters_estimation)

    if agent_type == 'f1':
        parameters_values_f1.append(new_parameters_estimation)

    if agent_type == 'f2':
        parameters_values_f2.append(new_parameters_estimation)

    return


def calculate_gradient_ascent(time_stamp, x_train, y_train,
                              old_parameter):  # p = parameter value at time t-1 and D is pair of (p,f(p)) in which p is the parameter value and f(p) is the probability of action a given the parameter p and other conditions (implementation of Algorithm 2 in the paper for updatint parameter value)

    print("start calculating gradient ascent")
    step_size = 0.5

    reg = linear_model.LinearRegression()
    print("x_train", x_train)
    print("y_train", y_train)
    reg.fit(x_train, y_train)

    gradient = reg.coef_

    print("gradient", gradient)

    new_parameters = old_parameter + gradient * step_size

    return new_parameters


def generate_data_for_update_parameter(agent_type, data_numbers):
    D = []  # D= (p,f(p)) , f(p) = P(a|H_t_1,teta,p)

    for i in range(0, data_numbers):
        # generating random values for parameters
        tmp_radius = (round(random.uniform(radius_min, radius_max), 2))  # 'radius'
        tmp_angle = (round(random.uniform(angle_min, angle_max), 2))  # 'angle'
        tmp_level = (round(random.uniform(level_min, level_max), 2))  # 'level'

        # tmp_radius = 0.48
        # tmp_angle = 0.42
        # tmp_level = 0.76

        sim = simulator.simulator.simulator(tmp_radius, tmp_angle, tmp_level)
        action_prob = sim.run()  # f(p)
        D.append([tmp_radius, tmp_angle, tmp_level, action_prob])

    return D


def main():
    initialisation()

    # for t in range(0, 10):
    selected_types = ['f2']

    for i in range(0, len(selected_types)):
        update_parameter_estimate(0, selected_types[i])

    #	for i in range(0, len(selected_types)):
    #		update_belief ((t, selected_types[i]))


main()
