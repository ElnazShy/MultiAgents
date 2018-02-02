import numpy as np
import parameter_estimation as est

if __name__ == "__main__":
    print("Beginning Approximate Bayesian Updating.")
    est.initialisation()
    selected_types = ['f2']
    for i in range(0, len(selected_types)):
        est.update_parameter_estimate(0, selected_types[i])
    #	for i in range(0, len(selected_types)):
    #		update_belief ((t, selected_types[i]))