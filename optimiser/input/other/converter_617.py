
# Libraries
import os
import pandas as pd

# content = "x,y,temp,stress,type,title\n0,0,800,60,creep,G32"

# Initialise
xlsx_files = [file for file in os.listdir() if file.endswith(".xlsx")]
condition_list = []

# Iterate through XLSX files
for xlsx_file in xlsx_files:


    # Extract data from file name
    file_list   = xlsx_file.split("_")
    file_start  = file_list[0]
    medium      = "Air" if file_start.startswith("Air") else "He"
    file_info   = file_start.replace("Air", "").replace("He", "").replace("MPa", "").split("C")
    temp        = int(file_info[0])
    stress      = int(file_info[1])
    
    # Identify sheet with data
    xl = pd.ExcelFile(xlsx_file)
    sheet_name = [sheet for sheet in xl.sheet_names if sheet.startswith("CreepStrainvsTime")][0]

    # Open XLSX file for reading
    data = pd.read_excel(io=xlsx_file, sheet_name=sheet_name)
    x_list = data.iloc[7:, 2].values.tolist()
    y_list = data.iloc[7:, 3].values.tolist()

    # Create new file name
    condition = f"{temp}_{stress}_{medium}"
    test_id   = condition_list.count(condition)+1
    new_file  = f"{condition}{test_id}"
    condition_list.append(condition)

    # Open file for writing
    new_fp = open(f"{new_file}.csv", "w+")

    # Write header
    new_fp.write("x,y,temp,stress,type,title\n")
    new_fp.write(f"0,0,{temp},{stress},creep,{medium}{test_id}\n")

    # Transfer x and y
    for i in range(len(x_list)):
        new_fp.write(f"{x_list[i]},{y_list[i]},,,\n")

    # Close
    new_fp.close()