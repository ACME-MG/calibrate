"""
 Title:         The y_end objective function
 Description:   The objective function for calculating the vertical distance in which two curves end
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
import modules.errors.__error__ as error

# The YEnd class
class YEnd(error.Error):

    # Constructor
    def __init__(self, type, exp_curves):
        super().__init__("y_end", type, exp_curves)
    
    # Prepares for evaluation
    def prepare(self):
        self.exp_y_end_list = [exp_curve["y"][-1] for exp_curve in self.exp_curves]
    
    # Computing the error
    def get_value(self, prd_curves):
        prd_y_end_list = [prd_curves[i]["y"][-1] for i in range(len(prd_curves))]
        value_list = [abs(prd_y_end_list[i] - self.exp_y_end_list[i]) / self.exp_y_end_list[i] for i in range(len(self.exp_y_end_list))]
        value_list = [value_list[i] if self.exp_curves[i]["type"] == self.type else 0 for i in range(len(value_list))]
        return np.average(value_list)