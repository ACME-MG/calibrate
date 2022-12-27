"""
 Title:         Reader
 Description:   For reading experimental data
 Author:        Janzen Choi

"""

# Libraries
import sys

# Helper Libraries
sys.path += ["../__common__", "../__models__"]
from excel import Excel
from __model__ import get_curve

# For reading experimental data
def get_exp_data(test_names, path, file):

    # Initialise
    excel = Excel(path=path, file=file)
    curve_list = []

    # Reads the experimental conditions
    temp_list       = excel.read_included("temp", test_names)
    stress_list     = excel.read_included("stress", test_names)
    type_list       = excel.read_included("type", test_names) 
    x_label_list    = excel.read_included("x_label", test_names)
    y_label_list    = excel.read_included("y_label", test_names)

    # Create curve objects
    for i in range(len(test_names)):
        x_list = excel.read_column(column = f"{test_names[i]}_{x_label_list[i]}", sheet = "data")
        y_list = excel.read_column(column = f"{test_names[i]}_{y_label_list[i]}", sheet = "data")
        curve = get_curve(
            x_list  = x_list,
            y_list  = y_list,
            x_label = x_label_list[i],
            y_label = y_label_list[i],
            type    = type_list[i],
            temp    = temp_list[i],
            stress  = stress_list[i],
            test    = test_names[i],
        )
        curve_list.append(curve)

    return curve_list