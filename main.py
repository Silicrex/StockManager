import os

import file_modification
import console_display
import command_flow_logic


def main():
    if not os.path.isfile('SMngr.dat'):
        print('SMngr.dat not detected. Attempting to generate...')
        file_modification.create_dat()
        print('SMngr.dat generated')

    line_data = file_modification.initialize_data()

    console_display.print_welcome(line_data)
    console_display.print_net(line_data)
    print()  # Newline to separate first input from printing

    while True:
        user_input = input().lower()
        if not user_input:  # It's possible to enter nothing
            continue
        if not user_input.isascii():
            print('Please only use ASCII characters')
            continue
        print()  # Newline to separate input from printing
        user_input = user_input.split()  # Split into a list of the command and parameters
        command_flow_logic.command_flow(line_data, user_input)
        print()  # Newline to separate input from printing


if __name__ == '__main__':
    main()
