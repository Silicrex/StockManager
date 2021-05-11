import ast

import core_dict_logic


def create_dat():
    with open('SMngr.dat', 'w') as file:
        template_dict = core_dict_logic.get_template_dict()
        for key, value in template_dict.items():
            file.write(f'{value}\n')


def initialize_data():
    with open('SMngr.dat', 'r') as file:  # Get list of all lines
        lines_list = file.readlines()
    lines = iter(lines_list)
    line_data = core_dict_logic.get_template_dict()  # Load template for structure
    for key in line_data:  # Fill each value line-by-line
        line_data[key] = ast.literal_eval(next(lines))
    with open('SMngr_backup.dat', 'w') as file:
        back_up(line_data, file)
    return line_data


def update(line_data):
    with open('SMngr.dat', 'w') as file:  # Writes line_data to file
        for key, value in line_data.items():
            file.write(f'{str(value)}\n')


def back_up(line_data, file):
    for key in line_data:
        file.write(f'{str(line_data[key])}\n')
