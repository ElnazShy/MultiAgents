import numpy as np
#from scipy.integrate import quad
import scipy.stats as st
#import parameter_estimation as est

dummy_d = [[0.0, -1.0, -1.0, 0], [0.01, -0.98, -0.98, 0], [0.02, -0.96, -0.96, 0], [0.03, -0.94, -0.94, 0],
           [0.04, -0.92, -0.92, 0], [0.05, -0.9, -0.9, 0], [0.06, -0.88, -0.88, 0], [0.07, -0.86, -0.86, 0],
           [0.08, -0.84, -0.84, 0], [0.09, -0.8200000000000001, -0.8200000000000001, 0], [0.1, -0.8, -0.8, 0],
           [0.11, -0.78, -0.78, 0], [0.12, -0.76, -0.76, 0], [0.13, -0.74, -0.74, 0], [0.14, -0.72, -0.72, 0],
           [0.15, -0.7, -0.7, 0], [0.16, -0.6799999999999999, -0.6799999999999999, 0],
           [0.17, -0.6599999999999999, -0.6599999999999999, 0], [0.18, -0.64, -0.64, 0], [0.19, -0.62, -0.62, 0],
           [0.2, -0.6, -0.6, 0], [0.21, -0.5800000000000001, -0.5800000000000001, 0], [0.22, -0.56, -0.56, 0],
           [0.23, -0.54, -0.54, 0], [0.24, -0.52, -0.52, 0], [0.25, -0.5, -0.5, 0], [0.26, -0.48, -0.48, 0],
           [0.27, -0.45999999999999996, -0.45999999999999996, 0], [0.28, -0.43999999999999995, -0.43999999999999995, 0],
           [0.29, -0.42000000000000004, -0.42000000000000004, 0], [0.3, -0.4, -0.4, 0], [0.31, -0.38, -0.38, 0],
           [0.32, -0.36, -0.36, 0], [0.33, -0.33999999999999997, -0.33999999999999997, 0],
           [0.34, -0.31999999999999995, -0.31999999999999995, 0],
           [0.35000000000000003, -0.29999999999999993, -0.29999999999999993, 0], [0.36, -0.28, -0.28, 0],
           [0.37, -0.26, -0.26, 0], [0.38, -0.24, -0.24, 0], [0.39, -0.21999999999999997, -0.21999999999999997, 0],
           [0.4, -0.19999999999999996, -0.19999999999999996, 0],
           [0.41000000000000003, -0.17999999999999994, -0.17999999999999994, 0],
           [0.42, -0.16000000000000003, -0.16000000000000003, 0], [0.43, -0.14, -0.14, 0], [0.44, -0.12, -0.12, 0],
           [0.45, -0.09999999999999998, -0.09999999999999998, 0], [0.46, -0.07999999999999996, -0.07999999999999996, 0],
           [0.47000000000000003, -0.05999999999999994, -0.05999999999999994, 0],
           [0.48, -0.040000000000000036, -0.040000000000000036, 0],
           [0.49, -0.020000000000000018, -0.020000000000000018, 0], [0.5, 0.0, 0.0, 0],
           [0.51, 0.020000000000000018, 0.020000000000000018, 0], [0.52, 0.040000000000000036, 0.040000000000000036, 0],
           [0.53, 0.06000000000000005, 0.06000000000000005, 0], [0.54, 0.08000000000000007, 0.08000000000000007, 0],
           [0.55, 0.10000000000000009, 0.10000000000000009, 0], [0.56, 0.1200000000000001, 0.1200000000000001, 0],
           [0.5700000000000001, 0.14000000000000012, 0.14000000000000012, 0],
           [0.58, 0.15999999999999992, 0.15999999999999992, 0], [0.59, 0.17999999999999994, 0.17999999999999994, 0],
           [0.6, 0.19999999999999996, 0.19999999999999996, 0], [0.61, 0.21999999999999997, 0.21999999999999997, 0],
           [0.62, 0.24, 0.24, 0], [0.63, 0.26, 0.26, 0], [0.64, 0.28, 0.28, 0],
           [0.65, 0.30000000000000004, 0.30000000000000004, 0.01],
           [0.66, 0.32000000000000006, 0.32000000000000006, 0.01], [0.67, 0.3400000000000001, 0.3400000000000001, 0.01],
           [0.68, 0.3600000000000001, 0.3600000000000001, 0.01],
           [0.6900000000000001, 0.3800000000000001, 0.3800000000000001, 0.01],
           [0.7000000000000001, 0.40000000000000013, 0.40000000000000013, 0.01],
           [0.71, 0.41999999999999993, 0.41999999999999993, 0.01], [0.72, 0.43999999999999995, 0.43999999999999995, 0.01],
           [0.73, 0.45999999999999996, 0.45999999999999996, 0.01], [0.74, 0.48, 0.48, 0.01], [0.75, 0.5, 0.5, 0.01],
           [0.76, 0.52, 0.52, 0.01], [0.77, 0.54, 0.54, 0.01], [0.78, 0.56, 0.56, 0.01],
           [0.79, 0.5800000000000001, 0.5800000000000001, 0.01], [0.8, 0.6000000000000001, 0.6000000000000001, 0.01],
           [0.81, 0.6200000000000001, 0.6200000000000001, 0.01],
           [0.8200000000000001, 0.6400000000000001, 0.6400000000000001, 0.01],
           [0.8300000000000001, 0.6600000000000001, 0.6600000000000001, 0.01],
           [0.84, 0.6799999999999999, 0.6799999999999999, 0.01], [0.85, 0.7, 0.7, 0.01], [0.86, 0.72, 0.72, 0.01],
           [0.87, 0.74, 0.74, 0.01], [0.88, 0.76, 0.76, 0.01], [0.89, 0.78, 0.78, 0.01], [0.9, 0.8, 0.8, 0.01],
           [0.91, 0.8200000000000001, 0.8200000000000001, 0.01], [0.92, 0.8400000000000001, 0.8400000000000001, 0.01],
           [0.93, 0.8600000000000001, 0.8600000000000001, 0.01],
           [0.9400000000000001, 0.8800000000000001, 0.8800000000000001, 0.01],
           [0.9500000000000001, 0.9000000000000001, 0.9000000000000001, 0.01],
           [0.96, 0.9199999999999999, 0.9199999999999999, 0.01], [0.97, 0.94, 0.94, 0.01], [0.98, 0.96, 0.96, 0.01],
           [0.99, 0.98, 0.98, 0.01]]


class BayesianUpdate:
    def __init__(self, X, y, degree=4):
        self.X = X
        self.y = y
        self.degree = degree
        self.meta_values ={'parameters':['Skill', 'View Radius', 'View Angle'],
                           'types':['Leader 1', 'Leader 2', 'Follower 1', 'Follower 2']}
        self.initial_values = self._initialise_values()
        self.print_values()

    def _initialise_values(self):
        """
        Takes three random samples from the standard uniform and sets these as the parameter's initial values.
        :return: Array of 3 floats, corresponding to the parameters initial values.
        """
        print('Initialising Values...')
        uniform_values = st.uniform.rvs(0, 1, size=3)
        return uniform_values

    def print_values(self, value='parameters'):
        """
        Prints the values of the updating method's current parameter/type estimate
        :param value: The specific value to be estimated. Likely to just be parameter or type
        :return: A printed list
        """
        if value in list(self.meta_values.keys()):
            print('Current {} Values (to 3.d.p):'.format(value.title()))
            item_names = self.meta_values[value]
            for i in range(len(item_names)):
                print('{} : {}'.format(item_names[i], self.initial_values[i]))
        else:
            print('Value parameter not present.\nCorresponding values could not be found.')

    def fit_polynomial(self):
        """
        Fits a polynomial of degree d to the features and labels.
        Future development may involved testing different values of d to try and minimise error.
        :return: A polynomial of degree d, stored as a class property
        """
        try:
            lm = np.polyfit(self.X, self.y, self.degree)
            self.lm = lm
            print("Polynomial successfully fitted")
        except:
            print("Polynomial could not be fitted.")

    def get_limits(self):
        """
        Calculates the lower and upper limits needed for integrations
        :return: list of lower and upper limit
        """
        limits = [np.amin(self.X), np.amax(self.X)]
        self.limits = limits

    def integrate_polynomial(self):
        """
        Computes the value of the definite integral of the data's fitted polynomial between the max and min of the data.
        :return: Float, sotred as class propert
        """
        self.get_limits()
        antideriv = np.polynomial.polyint(self.lm)
        upper_limit = np.polynomial.polyval(self.limits[1], antideriv)
        lower_limit = np.polynomial.polyval(self.limits[0], antideriv)
        integral_value = upper_limit-lower_limit
        self.integral_value = integral_value
        print("Integral Value: {}".format(self.integral_value))

    def new_belief(self):
        """
        To Do: Fit PDF to new beliefs and generate draws.
        :return:
        """
        belief = self.lm/self.integral_value

    def update(self):
        """
        Runs necessary in sequential order to run the ABU algorithm.
        :return: Class containing updated parameter estimates.
        """
        self.fit_polynomial()
        self.integrate_polynomial()

b = BayesianUpdate(1,2)