"""
 Title:         API for Surrogate Modelling
 Description:   For developing surrogate models
 Author:        Janzen Choi
 
"""

# Libraries
import time, sys, math, random
import matplotlib.pyplot as plt

# Helper libraries
sys.path += ["../__common__", "../__models__"]
from progressor import Progressor
from general import safe_mkdir
from __model_factory__ import get_model
from __model__ import get_curve

# I/O directories
INPUT_DIR   = "./input"
RESULTS_DIR = "./results"

# API Class
class API:

    # Constructor
    def __init__(self, fancy=False, title="", verbose=False):
        
        # Initialise
        self.prog = Progressor(fancy, title, verbose)
        self.plot_count = 1

        # Set up environment
        title = "" if title == "" else f" ({title})"
        self.output_dir  = time.strftime("%y%m%d%H%M%S", time.localtime(time.time()))
        self.output_path = f"{RESULTS_DIR}/{self.output_dir}{title}"
        safe_mkdir(RESULTS_DIR)
        safe_mkdir(self.output_path)

    # Defines the conditions of the creep (celcius and MPa)
    def define_conditions(self, info_dict={"type": "creep", "stress": 80, "temp": 800}):
        self.prog.add(f"Defining conditions")
        self.curve = get_curve([0], [0], info_dict)

    # Defines the model
    def define_model(self, model_name=""):
        self.prog.add(f"Defining the {model_name} model")
        self.model = get_model(model_name, [self.curve])
        self.param_names = self.model.get_param_names()
        self.l_bounds = self.model.get_param_lower_bounds()
        self.u_bounds = self.model.get_param_upper_bounds()
    
    # Assesses the values of individual parameters
    def assess_individual(self, trials=10):
        self.prog.add("Assessing individual parameters")

        # Create the plots
        num_params = len(self.param_names)
        plot_length = math.ceil(math.sqrt(num_params))
        figure, axis = plt.subplots(plot_length, plot_length)
        figure.set_size_inches(20, 10)
        figure.suptitle(f"Individual Parameter Assessment for {self.model.get_name()}")

        # Set titles
        for i in range(num_params):
            x_index, y_index = i//plot_length, i%plot_length
            axis[x_index, y_index].set_title(self.param_names[i])

        # Explore X points in the parameter space
        for trial in range(trials):
            
            # Generate random curve
            params = [random.uniform(self.l_bounds[i], self.u_bounds[i]) for i in range(len(self.l_bounds))]
            curve = self.model.get_prd_curves(*params)
            curve = {"x": curve[0]["x"], "y": curve[0]["y"]} if curve != [] else {"x": [], "y": []}

            # Test validity of curve
            if curve["x"] == [] or curve["y"] == []: # or curve["y"][-1] < 0.01:
                valid = False
            else:
                valid_list = [y >= 0 and y <= 1 for y in curve["y"]]
                valid = False not in valid_list
            
            # Plot parameter values
            for i in range(num_params):
                x_index, y_index = i//plot_length, i%plot_length
                value = 1 if valid else 0
                colour = "g" if valid else "r"
                axis[x_index, y_index].scatter([params[i]], [value], marker="o", color=colour, linewidth=1)
            
            # Save results
            figure.savefig(f"{self.output_path}/individual.png")
            print(f"  Explored {trial+1}/{trials}\t({'SUCCESS' if valid else 'FAILURE'})")
    
    # Assesses the parameter dependencies
    def assess_dependency(self, trials=10):
        self.prog.add("Assessing the parameter dependencies")

        # Create the plots
        num_params = len(self.param_names)
        figure, axis = plt.subplots(num_params, num_params)
        figure.set_size_inches(40, 40)
        figure.suptitle(f"Parameter Dependency Assessment for {self.model.get_name()}")

        # Set titles
        for i in range(num_params):
            for j in range(num_params):
                axis[i, j].set_title(f"{self.param_names[i]} : {self.param_names[j]}")

        # Explore X points in the parameter space
        for trial in range(trials):
            
            # Generate random curve
            params = [random.uniform(self.l_bounds[i], self.u_bounds[i]) for i in range(len(self.l_bounds))]
            curve = self.model.get_prd_curves(*params)
            curve = {"x": curve[0]["x"], "y": curve[0]["y"]} if curve != [] else {"x": [], "y": []}

            # Test validity of curve
            if curve["x"] == [] or curve["y"] == []: # or curve["y"][-1] < 0.01:
                valid = False
            else:
                valid_list = [y >= 0 and y <= 1 for y in curve["y"]]
                valid = False not in valid_list
            
            # Plot parameter values
            for i in range(num_params):
                for j in range(num_params):
                    colour = "g" if valid else "r"
                    axis[i, j].scatter([params[i]], [params[j]], marker="o", color=colour, linewidth=1)
            
            # Save results
            figure.savefig(f"{self.output_path}/dependency.png")
            print(f"  Explored {trial+1}/{trials}\t({'SUCCESS' if valid else 'FAILURE'})")
