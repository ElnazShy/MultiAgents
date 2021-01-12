import random
from numpy.random import choice
from sklearn import linear_model
import numpy as np

import agent
from random import sample
from scipy import stats

from copy import copy
import logging
import sys
import train_data
import POMCP_estimation

logging.basicConfig(filename='parameter_estimation.log', format='%(asctime)s %(message)s', level=logging.DEBUG)


radius_max = 1
radius_min = 0.1
angle_max = 1
angle_min = 0.1
level_max = 1
level_min = 0

########################################################################################################################
class Parameter:
    def __init__(self, level, angle, radius):
        self.level = level
        self.angle = angle
        self.radius = radius
        self.iteration = 0
        self.min_max = [(0, 1), (0.1, 1), (0.1, 1)]

    def update(self, added_value):
        self.level += added_value[0]
        self.angle += added_value[1]
        self.radius += added_value[2]
        return self


########################################################################################################################
class TypeEstimation:
    def __init__(self, a_type, generated_data_number, PF_add_threshold, train_mode, mutation_rate):
        self.type = a_type  # Type for which we are doing estimation
        self.type_probability = 0
        self.type_probabilities = []
        self.estimation_history = []
        self.action_probabilities = []
        self.internal_state = None
        self.train_mode = train_mode
        self.train_data = train_data.TrainData(generated_data_number, PF_add_threshold, train_mode, a_type,
                                               mutation_rate)

    ####################################################################################################################
    def add_estimation_history(self, probability, level, angle, radius):
        new_parameter = Parameter(level, angle, radius)
        self.estimation_history.append(new_parameter)
        self.type_probabilities.append(probability)

    ####################################################################################################################

    def get_estimation_history(self):
        estimation_history = "["
        for est_hist in self.estimation_history:
            estimation_history += "[" + str(est_hist.level) + "," + str(est_hist.angle) + "," + str(
                est_hist.radius) + "],"

        estimation_history = estimation_history[0:len(estimation_history) - 1]
        estimation_history += "]"
        return estimation_history

    ####################################################################################################################
    def get_last_type_probability(self):
        if len(self.type_probabilities) > 0:
            return self.type_probabilities[-1]
        else:
            return 1.0/5  ##todo: change it to the len of types

    ####################################################################################################################
    def get_last_estimation(self):
        if len(self.estimation_history) > 0:
            return self.estimation_history[-1]
        else:
            return sample(self.train_data.data_set,1)[0]
    
    ####################################################################################################################
    def get_last_action_probability(self):
        if len(self.action_probabilities) > 0:
            return self.action_probabilities[-1]
        else:
            return 0.2

    ####################################################################################################################
    def update_estimation(self, estimation, action_probability):
        self.estimation_history.append(estimation)
        self.action_probabilities.append(action_probability)
########################################################################################################################

class ParameterEstimation:

    def __init__(self,agent_types,  generated_data_number,
                 PF_add_threshold,
                 train_mode,
                 apply_adversary,
                  mutation_rate):

        # P(teta|H)
        self.agent_types = agent_types
        self.apply_adversary = apply_adversary
        if self.apply_adversary:
            self.w_estimation = TypeEstimation('w', generated_data_number, PF_add_threshold, train_mode, mutation_rate)

        self.type_estimations = []

        for t in self.agent_types:
            te = TypeEstimation(t, generated_data_number, PF_add_threshold, train_mode, mutation_rate)
            self.type_estimations.append(te)

        self.action_history = []
        self.train_mode = train_mode
        self.actions_to_reach_target = []
        # type_selection_mode are: all types selection 'AS', Posterior Selection 'PS' , Bandit Selection 'BS'
        self.type_selection_mode = None

        # Parameter estimation mode is AGA if it is Approximate Gradient Ascent ,
        #                              ABU if it is Approximate Bayesian Updating
        self.parameter_estimation_mode = None
        self.oeata_parameter_calculation_mode = None
        self.polynomial_degree = None

        self.iteration = 0
        self.alpha = 0.9
        self.belief_poly = [None] * 3

    ####################################################################################################################
    def get_parameters_for_selected_type(self, selected_type):

        for te in self.type_estimations:
            if selected_type == te.type:
                return te.get_last_estimation()


    ####################################################################################################################
    # Initialisation random values for parameters of each type and probability of actions in time step 0

    def estimation_configuration(self, type_selection_mode, parameter_estimation_mode, polynomial_degree,
                                 type_estimation_mode, oeata_parameter_calculation_mode = None):

        self.type_selection_mode = type_selection_mode
        self.parameter_estimation_mode = parameter_estimation_mode
        self.type_estimation_mode = type_estimation_mode
        self.polynomial_degree = polynomial_degree
        self.oeata_parameter_calculation_mode = oeata_parameter_calculation_mode

    ####################################################################################################################
    def generate_equal_probabilities(self):
        probabilities = []
        for i in range(0,len(self.type_estimations) - 1):
            te = self.type_estimations[i]
            probabilities.append(round(1.0 / len(self.agent_types), 2))

        probabilities.append( round( 1.0 - ((len(self.type_estimations) - 1) * (round(1.0 / len(self.agent_types), 2))),2))
        return probabilities

    ####################################################################################################################
    # Initialisation random values for parameters of each type and probability of actions in time step 0
    def estimation_initialisation(self):

        probabilities = self.generate_equal_probabilities()

        for i in range(0, len(self.type_estimations)):
            te = self.type_estimations[i]
            te.add_estimation_history(probabilities[i],
                                                  round(random.uniform(level_min, level_max), 2),  # 'level'
                                                  round(random.uniform(radius_min, radius_max), 2),  # 'radius'
                                                  round(random.uniform(angle_min, angle_max), 2))  # 'angle'

    ####################################################################################################################
    def get_sampled_probability(self):

        type_probes = list()
        for te in self.type_estimations:
            type_probes.append(te.get_last_type_probability())

        if self.apply_adversary:
            type_probes.append(self.w_estimation.get_last_type_probability())

        selected_type = choice(self.agent_types, p=type_probes)  # random sampling the action

        return selected_type


    #################################################################################################################
    def get_parameter(self, parameter, index):

        # TODO: Level = 0, angle = 1, radius = 2? Perhaps there should be a nicer way to do this

        if index == 0:
            return parameter.level
        if index == 1:
            return parameter.angle
        if index == 2:
            return parameter.radius

    ####################################################################################################################
    def findMin(self,polynomial):
        derivative = polynomial.deriv()

        roots = derivative.roots()

        minValue = sys.maxsize

        for r in roots:
            if polynomial(r) < minValue:
                minValue = polynomial(r)

        if polynomial(polynomial.domain[0]) < minValue:
            minValue = polynomial(polynomial.domain[0])

        if polynomial(polynomial.domain[1]) < minValue:
            minValue = polynomial(polynomial.domain[1])

        return minValue

    ####################################################################################################################
    def inversePolynomial(self,polynomialInput, y):
        solutions = list()

        polynomial = polynomialInput.copy()
        
        polynomial.coef[0] = polynomial.coef[0] - y

        roots = polynomial.roots()

        for r in roots:
            if (r >= polynomial.domain[0] and r <= polynomial.domain[1]):
                if (not (isinstance(r,complex))):
                    solutions.append(r)
                elif (r.imag == 0):
                    solutions.append(r.real)

        ## We should always have one solution for the inverse?
        if (len(solutions) > 1):
            print "Warning! Multiple solutions when sampling for ABU"
        
        return solutions[0]

    ####################################################################################################################
    # Inverse transform sampling
    # https://en.wikipedia.org/wiki/Inverse_transform_sampling
    def sampleFromBelief(self,polynomial,sizeList):
        returnMe = [None]*sizeList

        ## To calculate the CDF, I will first get the integral. The lower part is the lowest possible value for the domain
        ## Given a value x, the CDF will be the integral at x, minus the integral at the lowest possible value.
        dist_integ = polynomial.integ()
        lower_part = dist_integ(polynomial.domain[0])
        cdf = dist_integ.copy()
        cdf.coef[0] = cdf.coef[0] - lower_part
    
        for s in range(sizeList):
            u = np.random.uniform(0, 1)

            returnMe[s] = self.inversePolynomial(cdf, u)

        return returnMe

    ####################################################################################################################
    def nested_list_sum(self, nested_lists):
        if type(nested_lists) == list:
            return np.sum(self.nested_list_sum(sublist) for sublist in nested_lists)
        else:
            return 1

    ####################################################################################################################
    def UCB_selection(self, time_step, final=False):

        # Get the total number of probabilities
        prob_count = self.nested_list_sum(self.agent_types)

        # Return the mean probability for each type of bandit
        mean_probabilities = [np.mean(i) for i in self.agent_types]

        # Confidence intervals from standard UCB formula
        cis = [np.sqrt((2 * np.log(prob_count)) / len(self.agent_types[i]) + 0.01) for i in range(len(self.agent_types))]

        # Sum together means and CIs
        ucb_values = np.array(mean_probabilities) + np.array(cis)

        # Get max UCB value
        max_index = np.argmax(ucb_values)

        # Determine Agent Type to return
        try:
            if max_index == 0:
                return_agent = ['l1']
            elif max_index == 1:
                return_agent = ['l2']
            elif max_index == 2:
                return_agent = ['l3']
            elif max_index == 3:
                return_agent = ['l4']
            elif max_index == 4:
                return_agent = ['w']

            else:
                print('UCB has not worked correctly, defaulting to l1')
                return_agent = ['l1']
        except:
            print('An error has occured in UCB, resorting to l1')
            return_agent = ['l3']

        #print('UCB Algorithm returned agent of type: {}'.format(return_agent[0]))

        if final:
            return return_agent
        else:
            return ['l4']


    ####################################################################################################################

    def normalize_type_probabilities(self):
        # 1. Defining the values
        # print 'Normalizing:',self.l1_estimation.type_probability , self.l2_estimation.type_probability,self.l3_estimation.type_probability, self.l4_estimation.type_probability
        sum_of_probabilities = 0
        type_belief_values = []
        for te in self.type_estimations:
            type_belief_values.append(te.type_probability)
            sum_of_probabilities += te.type_probability

        # 3. Normalising
        if sum_of_probabilities != 0:
            belief_factor = 1 / float(sum_of_probabilities)
            for te in self.type_estimations:
                te.type_probability  *=  belief_factor
                te.type_probabilities.append(te.type_probability)

        else:
            probabilities = self.generate_equal_probabilities()
            for i in range(len(self.type_estimations)):
                self.type_estimations[i].type_probability = probabilities[i]
                self.type_estimations[i].type_probabilities.append(te.type_probability)

    ####################################################################################################################

    def get_highest_type_probability(self):

        highest_probability = -1
        selected_type = ''

        for te in self.type_estimations:
            tmp_prob =  te.get_last_type_probability()
            if tmp_prob > highest_probability:
                highest_probability = tmp_prob
                selected_type = type

        return selected_type
    ####################################################################################################################
    def bayesian_updating(self, x_train, y_train, previous_estimate,  polynomial_degree=2, sampling='average'):

        parameter_estimate = []

        for i in range(len(x_train[0])):
            # Get current independent variables
            current_parameter_set = [elem[i] for elem in x_train]

            # Obtain the parameter in questions upper and lower limits
            p_min = previous_estimate.min_max[i][0]
            p_max = previous_estimate.min_max[i][1]

            # Fit polynomial to the parameter being modelled
            f_poly = np.polynomial.polynomial.polyfit(current_parameter_set, y_train,
                                                              deg=polynomial_degree, full=False)
            
            f_poly = np.polynomial.polynomial.Polynomial(coef=f_poly, domain=[p_min, p_max], window=[p_min, p_max])
            
            # Generate prior
            if self.iteration == 0:
                #beliefs = st.uniform.rvs(0, 6AGA_O_2, size=polynomial_degree + 6AGA_O_2)
                beliefs = [0]*(polynomial_degree + 1)
                beliefs[0] = 1.0/(p_max - p_min)
                
                current_belief_poly = np.polynomial.polynomial.Polynomial(coef=beliefs, domain=[p_min, p_max], window=[p_min,p_max])
            else:
                current_belief_poly = self.belief_poly[i]
            

            # Compute convolution
            g_poly = current_belief_poly*f_poly

            # Collect samples
            # Number of evenly spaced points to compute polynomial at
            # TODO: Not sure why it was polynomial_degree + 6AGA_O_2
            # spacing = polynomial_degree + 6AGA_O_2
            spacing = len(x_train)

            # Generate equally spaced points, unique to the parameter being modelled
            X = np.linspace(p_min, p_max, spacing)
            y = np.array([g_poly(j) for j in X])

            # Future polynomials are modelled using X and y, not D as it's simpler this way. I've left D in for now
            # TODO: possilby remove D if not needed at the end
            D = [(X[j], y[j]) for j in range(len(X))]

            # Fit h
            h_hat_coefficients = np.polynomial.polynomial.polyfit(X, y, deg=polynomial_degree, full=False)
            
            h_poly = np.polynomial.polynomial.Polynomial(coef=h_hat_coefficients, domain=[p_min, p_max], window=[p_min, p_max])

            # "Lift" the polynomial. Perhaps this technique is different than the one in Albrecht and Stone 2017.
            min_h = self.findMin(h_poly)
            if min_h < 0:
                h_poly.coef[0] = h_poly.coef[0] - min_h

            # Integrate h
            integration = h_poly.integ()

            # Compute I
            definite_integral = integration(p_max) - integration(p_min)

            # Update beliefs
            new_belief_coef = np.divide(h_poly.coef, definite_integral)  # returns an array
            new_belief = np.polynomial.polynomial.Polynomial(coef=new_belief_coef,domain=[p_min, p_max],window=[p_min, p_max])

            self.belief_poly[i] = new_belief

            # TODO: Not better to derivate and get the roots?
            if sampling == 'MAP':
                # Sample from beliefs
                polynomial_max = 0
                granularity = 1000
                x_vals = np.linspace(p_min, p_max, granularity)
                for j in range(len(x_vals)):
                    proposal = new_belief(x_vals[j])
                    #print('Proposal: {}'.format(proposal))
                    if proposal > polynomial_max:
                        polynomial_max = proposal

                parameter_estimate.append(polynomial_max)

            elif sampling == 'average':
                x_random = self.sampleFromBelief(new_belief, 10)
                parameter_estimate.append(np.mean(x_random))

            # Increment iterator

        new_parameter = Parameter(parameter_estimate[0], parameter_estimate[1], parameter_estimate[2])
        #print('Parameter Estimate: {}'.format(parameter_estimate))
        self.iteration += 1

        return new_parameter

    ####################################################################################################################
    def calculate_gradient_ascent(self,x_train, y_train, old_parameter, polynomial_degree=2, univariate=True):
        # p is parameter estimation value at time step t-6AGA_O_2 and D is pair of (p,f(p))
        # f(p) is the probability of action which is taken by unknown agent with true parameters at time step t
        # (implementation of Algorithm 2 in the paper for updating parameter value)

        step_size = 0.05
        if not univariate:
            reg = linear_model.LinearRegression()
            reg.fit(x_train, y_train)
            gradient = reg.coef_

            # f_coefficients = np.polynomial.polynomial.polyfit(x_train, y_train,
            #                                                   deg=self.polynomial_degree, full=False)

            new_parameters = old_parameter.update(gradient * step_size)

            # Not sure if we need this rounding
            # new_parameters.level, new_parameters.angle, new_parameters.radius = \
            #    round(new_parameters.level, 2), round(new_parameters.angle, 2), round(new_parameters.radius, 2)

            if new_parameters.level < level_min:
                new_parameters.level = level_min

            if new_parameters.level > level_max:
                new_parameters.level = level_max

            if new_parameters.angle < angle_min:
                new_parameters.angle = angle_min

            if new_parameters.angle > angle_max:
                new_parameters.angle = angle_max

            if new_parameters.radius < radius_min:
                new_parameters.radius = radius_min

            if new_parameters.radius > radius_max:
                new_parameters.radius = radius_max

            return new_parameters
        
        else:
            parameter_estimate = []

            for i in range(len(x_train[0])):

                # Get current independent variables
                current_parameter_set = [elem[i] for elem in x_train]

                # Obtain the parameter in questions upper and lower limits
                p_min = old_parameter.min_max[i][0]
                p_max = old_parameter.min_max[i][1]

                # Fit polynomial to the parameter being modelled
                f_poly = np.polynomial.polynomial.polyfit(current_parameter_set, y_train,
                                                                  deg=polynomial_degree, full=False)

                f_poly = np.polynomial.polynomial.Polynomial(coef=f_poly, domain=[p_min, p_max], window=[p_min, p_max])

                # get gradient
                f_poly_deriv = f_poly.deriv()

                current_estimation = self.get_parameter(old_parameter,i)
                
                delta = f_poly_deriv(current_estimation)

                # update parameter
                new_estimation = current_estimation + step_size*delta

                if (new_estimation < p_min):
                    new_estimation = p_min
                if (new_estimation > p_max):
                    new_estimation = p_max

                parameter_estimate.append(new_estimation)
            return Parameter(parameter_estimate[0], parameter_estimate[1], parameter_estimate[2])

    ####################################################################################################################
    def mean_estimation(self, x_train,y_train):# y_train is weight of parameters which are equal to
        a_data_set = np.transpose(np.array(x_train))
        # print y_train
        if a_data_set != []:
            a_weights = np.array(y_train)
            levels = a_data_set[0, :]
            # ave_level = np.average(levels, weights=a_weights)
            ave_level = np.average(levels)
            angle = a_data_set[1, :]
            # ave_angle = np.average(angle, weights=a_weights)
            ave_angle = np.average(angle)
            radius = a_data_set[2, :]
            # ave_radius = np.average(radius, weights=a_weights)
            ave_radius = np.average(radius)
            new_parameter = Parameter(ave_level, ave_angle, ave_radius)

            return new_parameter
        else:
            return None

    ####################################################################################################################
    def mode_estimation(self, x_train, y_train):  # y_train is weight of parameters which are equal to
        a_data_set = np.transpose(np.array(x_train))
        # print y_train
        if a_data_set != []:
#            a_weights = np.mod(y_train)
            levels = a_data_set[0, :]
            ave_level = stats.mode(levels)[0][0]
            angle = a_data_set[1, :]
            # ave_angle = np.average(angle, weights=a_weights)
            ave_angle = stats.mode(angle)[0][0]
            radius = a_data_set[2, :]
            # ave_radius = np.average(radius, weights=a_weights)
            ave_radius = stats.mode(radius)[0][0]
            new_parameter = Parameter(ave_level, ave_angle, ave_radius)
            print stats.mode(levels)[0]
            # if a_data_set != []:
            #     levels = a_data_set[0, :]
            #     ave_level = np.average(levels)
            #
            #     angle = a_data_set[1, :]
            #     ave_angle = np.average(angle)
            #
            #     radius = a_data_set[2, :]
            #     ave_radius = np.average(radius)
            #
            #     new_parameter = Parameter(ave_level, ave_angle, ave_radius)
            return new_parameter
        else:
            return None

    ####################################################################################################################
    def median_estimation(self, x_train, y_train):  # y_train is weight of parameters which are equal to
        a_data_set = np.transpose(np.array(x_train))
        # print y_train
        if a_data_set != []:
            # a_weights = np.mod(y_train)
            levels = a_data_set[0, :]
            ave_level = np.median(levels)
            angle = a_data_set[1, :]
            # ave_angle = np.average(angle, weights=a_weights)
            ave_angle = np.median(angle)
            radius = a_data_set[2, :]
            # ave_radius = np.average(radius, weights=a_weights)
            ave_radius = np.median(radius)
            new_parameter = Parameter(ave_level, ave_angle, ave_radius)

            return new_parameter
        else:
            return None

    ####################################################################################################################
    def copy_last_estimation(self, agent_type):

        for te in self.type_estimations:
            if te.type == agent_type:
               return copy(te.get_last_estimation())

        return None

    ####################################################################################################################
    def parameter_estimation(self, x_train, y_train, agent_type):
        # 1. Getting the last agent parameter estimation
        last_parameters_value = self.copy_last_estimation(agent_type)

        # 2. Running the estimation method if the train data
        # sets are not empty
        estimated_parameter = None
        if x_train != [] and y_train != []:
            if self.parameter_estimation_mode == 'MIN' :
                if self.oeata_parameter_calculation_mode =='MEAN':
                    estimated_parameter = self.mean_estimation(x_train,y_train)
                if self.oeata_parameter_calculation_mode == 'MODE':
                    estimated_parameter = self.mode_estimation(x_train, y_train)
                if self.oeata_parameter_calculation_mode =='MEDIAN':
                    estimated_parameter = self.median_estimation(x_train,y_train)
            elif self.parameter_estimation_mode == 'AGA':
                estimated_parameter = self.calculate_gradient_ascent(x_train, y_train, last_parameters_value)
            elif self.parameter_estimation_mode == 'ABU':
                estimated_parameter = self.bayesian_updating(x_train, y_train, last_parameters_value)


        else:
            estimated_parameter = last_parameters_value

        return estimated_parameter

    ####################################################################################################################
    def get_last_selected_type_probability(self,selected_type):

        for te in self.type_estimations:
            if selected_type == te.type:
                return te.get_last_type_probability()

        return 0

    ####################################################################################################################
    def update_internal_state(self, parameters_estimation, selected_type, unknown_agent, po):
        # 1. Defining the agent to update in main agent point of view
        u_agent = None 
        if not po:
            for v_a in unknown_agent.choose_target_state.main_agent.visible_agents:
                if v_a.index == unknown_agent.index:
                    u_agent = v_a

        else:
            memory_agents = unknown_agent.choose_target_state.main_agent.agent_memory
            for m_a in memory_agents:
                if m_a.index == unknown_agent.index:
                    u_agent = m_a
                    break

        # 2. Creating the agents for simulation
        tmp_sim = copy(unknown_agent.choose_target_state)
        (x,y), direction = u_agent.get_position(),u_agent.direction 
        tmp_agent = agent.Agent(x,y,direction,selected_type,-1)
        tmp_agent.set_parameters(tmp_sim,parameters_estimation.level,parameters_estimation.radius,parameters_estimation.angle)

        # 3. Finding the target
        tmp_agent.visible_agents_items(tmp_sim.items, tmp_sim.agents)
        target = tmp_agent.choose_target(tmp_sim.items, tmp_sim.agents)

        self.iteration += 1
        return target

    ####################################################################################################################
    def copy_train_data(self, selected_type):
        if selected_type == 'l1':
            return copy(self.l1_estimation.train_data)
        elif selected_type == 'l2':
            return copy(self.l2_estimation.train_data)
        elif selected_type == 'l3':
            return copy(self.l3_estimation.train_data)
        elif selected_type == 'l4':
            return copy(self.l4_estimation.train_data)
        elif selected_type == 'w':
            return copy(self.w_estimation.train_data)
        else:
            return None

    ####################################################################################################################
    def get_train_data(self, selected_type):
        for te in self.type_estimations:
            if selected_type == te.type:
                return copy(te.train_data)

        return None

    ####################################################################################################################
    def update_train_data(self, u_a, previous_state, current_state, selected_type,loaded_items_list, po):
        # 1. Copying the selected type train data
        # unknown_agent = deepcopy(u_a)
        unknown_agent = (u_a)
        max_suceed_cts = None
        train_data = self.get_train_data(selected_type)
        max_succeed_cts = None
        # 2. Updating th Particles
        type_probability = self.get_last_selected_type_probability(selected_type)
        if self.train_mode == 'history_based':
            if unknown_agent.next_action == 'L':
                type_probability , max_succeed_cts = train_data.evaluate_data_set(unknown_agent,current_state,po)
                train_data.generate_data(unknown_agent, selected_type,current_state )

                # b. Generating
            else:
                train_data.update_data_set(unknown_agent,loaded_items_list,current_state,po)
        else:
            self.data = train_data.\
                generate_data_for_update_parameter(previous_state,unknown_agent,selected_type, po)

        # 3. Updating the estimation train data
        for te in self.type_estimations:
            if selected_type == te.type:
                te.train_data = copy(train_data)

        # 4. Extrating and returning the train set
        x_train, y_train = train_data.extract_train_set()
        return x_train, y_train, type_probability , max_succeed_cts

    ####################################################################################################################
    def POMCP_estimation(self,curren_state):
        iteration_max= 100
        max_depth = 100
        particle_filter_numbers = 100

        pomcpe = POMCP_estimation.POMCP(iteration_max, max_depth,particle_filter_numbers)
        estimated_parameter, estimated_type = pomcpe.start_estimation (None,  curren_state)
        return estimated_parameter.tolist(), estimated_type

    ####################################################################################################################
    def process_parameter_estimations(self, unknown_agent,previous_state,
    current_state, enemy_action_prob, types,loaded_items_list, po=False):
        # 1. Initialising the parameter variables

        max_succeed_cts = None

        if self.parameter_estimation_mode == 'POMCP' :
            estimated_parameter, estimated_type = self.POMCP_estimation(current_state)
            estimated_parameter = Parameter(estimated_parameter[0], estimated_parameter[1], estimated_parameter[2])
            for te in self.type_estimations:
                te.type_probability =1
                te.estimation_history.append(estimated_parameter)
        else :
            # print '>>>>>',po
            # 2. Estimating the agent type
            for selected_type in types:
                # a. updating the train data for the current state
                x_train, y_train, pf_type_probability,max_succeed_cts = \
                self.update_train_data(unknown_agent,
                    previous_state, current_state, selected_type,loaded_items_list,po)

                # b. estimating the type with the new train data
                new_parameters_estimation = \
                self.parameter_estimation(x_train, y_train, selected_type)

                # c. considering the new estimation
                if new_parameters_estimation is not None:
                    # i. generating the particle for the selected type
                    if selected_type != 'w': # If the selected type is not
                        tmp_sim = previous_state.copy()
                        # print '*********previous state in simulation*******'
                        # tmp_sim.draw_map()

                        x = unknown_agent.previous_agent_status.position[0]
                        y = unknown_agent.previous_agent_status.position[1]
                        direction = unknown_agent.previous_agent_status.direction
                        tmp_agent = agent.Agent(x, y, direction,-1, selected_type)

                        tmp_agent.set_parameters(tmp_sim, new_parameters_estimation.level,
                            new_parameters_estimation.radius,new_parameters_estimation.angle)
                        tmp_agent.memory = self.update_internal_state(new_parameters_estimation,
                            selected_type,unknown_agent,po)

                        # Runs a simulator object
                        tmp_agent = tmp_sim.move_a_agent(tmp_agent)
                        action_prob = tmp_agent.get_action_probability(unknown_agent.next_action)
                        # print selected_type, tmp_agent.memory.get_position(),action_prob
                        # print '*******************************************'
                        if action_prob is None:
                            action_prob = 0.2
                        # print action_prob
                        # ii. testing the generated particle and updating the estimation

                        for te in self.type_estimations:
                            if te.type == selected_type:
                                if self.train_mode == 'history_based':
                                    if self.type_estimation_mode == 'BTE':
                                        te.type_probability = action_prob * te.get_last_type_probability()
                                    if self.type_estimation_mode == 'PTE' or self.type_estimation_mode == 'BPTE':
                                        te.type_probability = pf_type_probability
                                else:
                                    te.type_probability = action_prob * te.get_last_type_probability()

                                te.update_estimation(new_parameters_estimation, action_prob)


                    # ADVERSARY ------------------
                    # else:
                    #     if self.train_mode == 'history_based':
                    #         self.w_estimation.type_probability = enemy_action_prob * self.w_estimation.get_last_type_probability()
                    #     else:
                    #         self.w_estimation.type_probability = enemy_action_prob * self.w_estimation.get_last_type_probability()
                    #     self.w_estimation.update_estimation(new_parameters_estimation, enemy_action_prob)

            # d. If a load action was performed, restart the estimation process
            if unknown_agent.next_action == 'L' and unknown_agent.is_item_nearby(current_state.items) != -1:
                if unknown_agent.choose_target_state != None and max_succeed_cts != None:
                    hist = {}
                    hist['pos'] = copy(unknown_agent.choose_target_pos)
                    hist['direction'] = unknown_agent.choose_target_direction
                    # hist['state'] = max_succeed_cts # unknown_agent.choose_target_state.copy()  # todo: replace it with items and agents position instead of whole state!
                    hist['state'] =  unknown_agent.choose_target_state.copy()
                    hist['loaded_item'] = copy(unknown_agent.last_loaded_item_pos)
                    unknown_agent.choose_target_history.append(hist)

                unknown_agent.choose_target_state = current_state.copy()
                unknown_agent.choose_target_pos = unknown_agent.get_position()
                unknown_agent.choose_target_direction = unknown_agent.direction

            # e. Normalising the type probabilities
            if self.train_mode == 'history_based':
                if self.type_estimation_mode == 'BPTE':
                    self.normalize_type_probabilities()
                    for te in self.type_estimations:
                        te.type_probability = te.type_probability * te.get_last_type_probability()

        self.normalize_type_probabilities()
