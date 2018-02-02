import random
import agent
from sklearn import linear_model

radius_max = 1
radius_min = -1
angle_max = 1
angle_min = -1
level_max = 1
level_min = 0


class ParameterEstimation:

    def __init__(self):
        types = ['l1', 'l2', 'f1', 'f2']

        # P(teta|H)
        self.p_type_l1 = []
        self.p_type_l2 = []
        self.p_type_f1 = []
        self.p_type_f2 = []

        # P(a|H,teta,p)
        self.p_action_parameter_type_l1 = []
        self.p_action_parameter_type_l2 = []
        self.p_action_parameter_type_f1 = []
        self.p_action_parameter_type_f2 = []

        self.parameters_values_l1 = []
        self.parameters_values_l2 = []
        self.parameters_values_f1 = []
        self.parameters_values_f2 = []

    @staticmethod
    def create_random_parameters():
        tmp_parameter = list()
        tmp_parameter.append(round(random.uniform(level_min, level_max), 2))  # 'level'
        tmp_parameter.append(round(random.uniform(radius_min, radius_max), 2))  # 'radius'
        tmp_parameter.append(round(random.uniform(angle_min, angle_max), 2))  # 'angle'

        return tmp_parameter

    # Initialisation random values for parameters of each type and probability of actions in time step 0
    def estimation_initialisation(self):
        # P(teta|H) in t = 0
        self.p_type_l1.append(round(random.uniform(0, 1), 1))
        self.p_type_l2.append(round(random.uniform(0, 1), 1))
        self.p_type_f1.append(round(random.uniform(0, 1), 1))
        self.p_type_f2.append(round(random.uniform(0, 1), 1))

        # parameters estimated values for each type
        self.parameters_values_l1.append(self.create_random_parameters())
        self.parameters_values_l2.append(self.create_random_parameters())
        self.parameters_values_f1.append(self.create_random_parameters())
        self.parameters_values_f2.append(self.create_random_parameters())

    # =================Generating  D = (p,f(p)) , f(p) = P(a|H_t_1,teta,p)=========================
    @staticmethod
    def generate_data_for_update_parameter(sim, tmp_agent, data_numbers, action):

        # print '*********************************************************************************'
        # print '******generating data for updating parameter *******'

        D = []  # D= (p,f(p)) , f(p) = P(a|H_t_1,teta,p)

        for i in range(0, data_numbers):

            # Generating random values for parameters
            # tmp_radius = (round(random.uniform(radius_min, radius_max), 2))  # 'radius'
            # tmp_angle = (round(random.uniform(angle_min, angle_max), 2))  # 'angle'
            # tmp_level = (round(random.uniform(level_min, level_max), 2))  # 'level'

            tmp_radius = radius_min + (1.0 *(radius_max - radius_min) / data_numbers) * i
            tmp_angle = angle_min + (1.0 *(angle_max - angle_min) / data_numbers) * i
            tmp_level = level_min + (1.0 *(level_max - level_min) / data_numbers) * i

            # print "parameters for data generetion step " + str(i) + " is " + str (tmp_radius) + "," + str (tmp_angle) + "," + str(tmp_level)

            tmp_agent.set_parameters(tmp_level, tmp_radius, tmp_angle)

            tmp_agent = sim.run(tmp_agent)  # f(p)
            p_action = tmp_agent.get_action_probability(action)

            # Print 'action probability',p_action , 'for action ', action , '  when running temp agent number ', i
            if p_action is not None:
                D.append([tmp_level,tmp_radius, tmp_angle,  p_action])

        #print 'gathered data :     ', D
       # print '******End of generating data for updating parameter *******'
       # print '*********************************************************************************'
        print("Parameters D: {}".format(D))
        return D

    @staticmethod
    def calculate_gradient_ascent(x_train, y_train, old_parameter):
        # p is parameter estimation value at time step t-1 and D is pair of (p,f(p))
        # f(p) is the probability of action which is taken by unknown agent with true parameters at time step t
        # (implementation of Algorithm 2 in the paper for updating parameter value)

       # print
       # print "**** start calculating gradient ascent ***"
       # print
        # print 'x_train:  ', x_train, '  y_train:  ', y_train

        step_size = 0.5

        reg = linear_model.LinearRegression()

        reg.fit(x_train, y_train)

        gradient = reg.coef_

        new_parameters = old_parameter + gradient * step_size

        return new_parameters

    def calculate_EGO(self,agent_type,time_step):  # Exact Global Optimisation

        multiple_results = 1
        if agent_type.agent_type == 'l1':
            for i in range(0,time_step):
                multiple_results = multiple_results * self.p_action_parameter_type_l1[i]

        if agent_type.agent_type == 'l2':
            self.p_action_parameter_type_l2 = []
        if agent_type.agent_type == 'f1':
            self.p_action_parameter_type_f1 = []

        if agent_type.agent_type == 'f2':
            self.p_action_parameter_type_f2 = []


        return

    def parameter_estimation(self,time_step, cur_agent, sim, action):

        data_numbers = 100
        #print '***********************************************************************************************'
       # print 'Start  Updating parameter estimation'

        D = self.generate_data_for_update_parameter(sim, cur_agent, data_numbers, action)
        #print D
        x_train = []
        y_train = []

        if len(D) == 0:
            return

        # Extract x, y train from generated data
        for i in range(0,data_numbers):
            x_train.append(D[i][0:3])
            y_train.append(D[i][3])
            # get the value of p in t-1

        last_parameters_value = 0

        if cur_agent.agent_type == 'l1':
            last_parameters_value = self.parameters_values_l1[time_step - 1]

        if cur_agent.agent_type == 'l2':
            last_parameters_value = self.parameters_values_l2[time_step - 1]

        if cur_agent.agent_type == 'f1':
            last_parameters_value = self.parameters_values_f1[time_step - 1]

        if cur_agent.agent_type == 'f2':
            last_parameters_value = self.parameters_values_f2 [time_step - 1]

        # parameters value order is : radius , angle, level
        estimated_parameters = self.calculate_gradient_ascent(x_train, y_train, last_parameters_value)
        # D = (p,f(p)) , f(p) = P(a|H_t_1,teta,p)

        ##print '***********************************************************************************************'
        return estimated_parameters

    def update_belief(self,t,agent_type):

        if agent_type == 'l1':
            self.p_type_l1.append(self.p_type_l1[t - 1] * self.p_action_parameter_type_l1[t - 1])

        if agent_type == 'l2':
            self.p_type_l2.append(self.p_type_l2[t - 1] * self.p_action_parameter_type_l2[t - 1])

        if agent_type == 'f1':
            self.p_type_f1.append(self.p_type_f1[t - 1] * self.p_action_parameter_type_f1[t - 1])

        if agent_type == 'f2':
            self.p_type_f2.append(self.p_type_f2[t - 1] * self.p_action_parameter_type_f2[t - 1])

    def update_internal_state(self):
        t = 0
        #sim = simulator.simulator(map_history[0], initial_items, initial_agents, n, m)


    def UCB_selection(self):
        return ['l1']

    def process_parameter_estimations(self, time_step, tmp_sim,  agent_position, action):

        # Start parameter estimation
        selected_types = self.UCB_selection()
        (x, y) = agent_position

        for i in range(0, len(selected_types)):

            # estimate the parameters
            tmp_agent = agent.Agent(x, y, selected_types[i], -1)

            new_parameters_estimation = self.parameter_estimation(time_step, tmp_agent, tmp_sim,   action)

            # moving temp agent in previous map with new parameters

            tmp_agent.set_parameters(new_parameters_estimation[0], new_parameters_estimation[1], new_parameters_estimation[2])

            tmp_sim.run(tmp_agent)
            action_prob = tmp_agent.get_action_probability(action)


            self.update_internal_state()

            if selected_types[i] == 'l1':
                self.parameters_values_l1.append(new_parameters_estimation)
                self.p_action_parameter_type_l1.append(action_prob)

            if selected_types[i] == 'l2':
                self.parameters_values_l2.append(new_parameters_estimation)
                self.p_action_parameter_type_l2.append(action_prob)

            if selected_types[i] == 'f1':
                self.parameters_values_f1.append(new_parameters_estimation)
                self.p_action_parameter_type_f1.append(action_prob)

            if selected_types[i] == 'f2':
                self.parameters_values_f2.append(new_parameters_estimation)
                self.p_action_parameter_type_f2.append(action_prob)

            self.update_belief(time_step ,  selected_types[i] )

        return new_parameters_estimation