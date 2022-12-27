"""
 Title:         Model
 Description:   Contains the basic structure for a model class
 Author:        Janzen Choi

"""

# Libraries
import os, sys

# Constants
NEML_SYSTEM_PATH = "/home/janzen/moose/neml"
# NEML_SYSTEM_PATH = "/home/choij/neml"

# The Model Class
class Model:

    # Constructor
    def __init__(self, name, param_info, exp_curves):
        self.name = name
        self.param_info = param_info
        self.exp_curves = exp_curves

    # Returns the name of the model
    def get_name(self):
        return self.name

    # Returns the parameter info
    def get_param_info(self):
        return self.param_info

    # Returns the parameter names
    def get_param_names(self):
        return [param["name"] for param in self.param_info]

    # Returns the parameter lower bounds
    def get_param_lower_bounds(self):
        return [param["min"] for param in self.param_info]

    # Returns the parameter upper bounds
    def get_param_upper_bounds(self):
        return [param["max"] for param in self.param_info]
    
    # Returns the experimental curves
    def get_exp_curves(self):
        return self.exp_curves
    
    # Gets the predicted curves (to be overriden)
    def get_prd_curves(self):
        return [get_curve([], []) for _ in range(len(self.exp_curves))] # do not remove [], []

# Returns a curve dictionary
def get_curve(x_list=[], y_list=[], x_label="", y_label="", type="", stress=0, temp=0, test=""):
    return {
        "x":        x_list,
        "y":        y_list,
        "x_label":  x_label,
        "y_label":  y_label,
        "type":     type,
        "stress":   stress,
        "temp":     temp,
        "test":     test,
    }

# For blocking prints
class BlockPrint:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def __exit__(self, _1, _2, _3):
        sys.stdout.close()
        sys.stdout = self._original_stdout