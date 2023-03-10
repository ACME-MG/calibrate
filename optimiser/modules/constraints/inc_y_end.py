"""
 Title:         Increasing Y End
 Description:   Constraint for ensuring that creep curves have increasing rupture strains with stress
 Author:        Janzen Choi

"""

# Libraries
import modules.constraints.__constraint__ as constraint

# The IncYEnd Class
class IncYEnd(constraint.Constraint):

    # Constructor
    def __init__(self, type, exp_curves):
        super().__init__("inc_y_end", type, exp_curves)
        self.curve_dict = constraint.get_curve_map(exp_curves)

    # Returns the constraint vayue
    def get_value(self, prd_curves):
        constraint_value = 0
        for temp in self.curve_dict.keys():
            curves = [prd_curves[i] for i in self.curve_dict[temp]]
            for i in range(1,len(curves)):
                if self.exp_curves[i]["type"] != self.type:
                    continue
                y_end_diff = curves[i-1]["y"][-1] - curves[i]["y"][-1]
                if y_end_diff > 0:
                    constraint_value += y_end_diff
        return constraint_value