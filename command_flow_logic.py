import datetime

import core_dict_logic
import file_modification
import console_display
import documentation
import history_interface
import live_price_info

# main gets input
# -> command_flow for parameter confirmation and sorting
# -> core_dict_logic for performing the tasks


def command_flow(line_data, user_input):
    def wrong_parameter_count(*expected):
        # Convert to list of len # instead of parameter #'s. List for pop() and list comprehension convenience
        expected = [x + 1 for x in expected]
        if input_length not in expected:
            print(f'Invalid amount of parameters (expected {expected.pop(0) - 1}', end='')  # Pop to check for more
            if expected:  # If there are more term numbers left after popping the first one
                for value in expected:
                    print(' or', value, end='')  # Print 'or x' for them all
            print(')')  # Print the close-parenthesis and newline
            return True  # Return True, as in to say there were a wrong # of terms
        return False  # Else return False, as in not wrong #

    # def invalid_parameter(parameter_number, *expected):  # Takes which parameter # and what was expected
    #     # expected should be a list of potential expected words
    #     expected = list(expected)  # List so we can use pop()
    #     print(f'Invalid parameter #{parameter_number}. Expected "{expected.pop(0)}"', end='')
    #     while expected:  # If there are more words left
    #         if len(expected) > 1:  # If it isn't the last one
    #             print(f', "{expected.pop(0)}"', end='')
    #         else:  # Last one
    #             print(f', or "{expected.pop(0)}"', end='')
    #     print()  # Newline

    input_length = len(user_input)
    command = user_input[0]

    if command in {'buy', 'b'}:
        if wrong_parameter_count(3, 4):
            return
        name = user_input[2]
        try:
            quantity = eval(user_input[1])
            cost = eval(user_input[3])
        except (NameError, SyntaxError, TypeError):
            print('Invalid input')
            return

        if input_length == 4:
            if not core_dict_logic.buy(line_data, name, quantity, cost):
                return
        else:  # input_length == 5
            date = user_input[4]
            # validate_date returns a formatted string or False
            if not (date := core_dict_logic.validate_date(date)):
                print('Invalid date. Expected YEAR-MONTH-DAY, including dashes (ex: 2021-04-01)')
                return
            if not core_dict_logic.buy(line_data, name, quantity, cost, date):
                return

        core_dict_logic.sort_current(line_data)
        file_modification.update(line_data)
        console_display.print_net(line_data)

    elif command in {'sell', 's'}:
        if wrong_parameter_count(3):
            return
        name = user_input[2]
        try:
            quantity = eval(user_input[1])
            cost = eval(user_input[3])
        except (NameError, SyntaxError, TypeError):
            print('Invalid input')
            return

        if not core_dict_logic.sell(line_data, name, quantity, cost):
            return

        core_dict_logic.sort_current(line_data)
        file_modification.update(line_data)
        console_display.print_net(line_data)

    elif command in {'fee', 'f'}:
        if wrong_parameter_count(2):
            return
        name = user_input[1]
        try:
            amount = eval(user_input[2])
        except (NameError, SyntaxError, TypeError):
            print('Invalid input')
            return

        if not core_dict_logic.fee_item(line_data, name, amount):
            return

        file_modification.update(line_data)
        console_display.print_net(line_data)

    elif command in {'dividend', 'div', 'd'}:
        if wrong_parameter_count(2):
            return

        name = user_input[1]
        try:
            amount = eval(user_input[2])
        except (NameError, SyntaxError, TypeError):
            print('Invalid input')
            return

        if not core_dict_logic.dividend_item(line_data, name, amount):
            return

        file_modification.update(line_data)
        console_display.print_net(line_data)

    elif command == 'list':
        if wrong_parameter_count(0):
            return
        console_display.print_current(line_data)

    elif command == 'net':
        if wrong_parameter_count(0):
            return
        console_display.print_net(line_data)

    elif command in {'adjustednet', 'anet', 'an'}:
        if wrong_parameter_count(0):
            return
        console_display.print_adjusted_net(line_data)

    elif command == '$':
        if wrong_parameter_count(0):
            return
        console_display.print_current_prices(line_data)

    elif command == 'peaks':
        if wrong_parameter_count(0):
            return
        console_display.print_peaks(line_data)

    elif command == 'high':
        if wrong_parameter_count(0):
            return
        console_display.print_highs(line_data)

    elif command == 'low':
        if wrong_parameter_count(0):
            return
        console_display.print_lows(line_data)

    elif command in {'expand', 'e'}:
        if wrong_parameter_count(1):
            return
        history = line_data['history']
        name = user_input[1]
        if name not in history:
            if not (name := core_dict_logic.item_search(name, history, line_data['settings']['auto_match_toggle'])):
                return
        try:
            live_price = live_price_info.get_stock_price(name)
        except IndexError:
            return
        net_value = core_dict_logic.calculate_history_net(line_data, name, live_price)
        console_display.print_expanded(line_data, name, live_price, net_value)

    elif command in {'history', 'h'}:
        if wrong_parameter_count(0):
            return
        history_interface.print_history(line_data)

    elif command in {'watchlist', 'wl'}:
        if wrong_parameter_count(0, 1, 2):
            return

        if input_length == 1:  # Just printing
            console_display.print_watchlist(line_data)
            return

        mode = user_input[1]

        if input_length == 2:  # Peaks, week, or month
            if mode in {'peaks', 'peak', 'p'}:
                console_display.print_watchlist(line_data, mode='peaks')
            else:
                print("Invalid parameter. Expected 'peaks'")
                return
        elif input_length == 3:  # Add/remove
            item = user_input[2]
            if mode not in {'add', 'remove'}:
                print("Invalid parameter. Expected 'add' or 'remove'")
                return

            if mode == 'add':
                if not core_dict_logic.watchlist_add(line_data, item):
                    return

            elif mode == 'remove':
                if not core_dict_logic.watchlist_remove(line_data, item):
                    return

            line_data['watchlist'] = sorted(line_data['watchlist'])
            file_modification.update(line_data)
            console_display.print_watchlist(line_data)

    elif command == 'backup':
        if wrong_parameter_count(0):
            return
        with open('SMngr_manual_backup.dat', 'w') as file:
            file_modification.back_up(line_data, file)
        print('Manual backup created')

    elif command == 'start':
        if wrong_parameter_count(0, 1):
            return

        if line_data['start']:  # It's already set
            print('Start date already set. Change manually in dat file if necessary')
            return

        if input_length == 1:  # No date given
            date = str(datetime.date.today())
        else:  # Date given
            date = user_input[1]
            if not (date := core_dict_logic.validate_date(date)):
                print('Invalid date')
                return
        line_data['start'] = (date,)
        file_modification.update(line_data)
        print('Started on', date)

    elif command == 'remove':
        if wrong_parameter_count(2):
            return
        dictionary_input = user_input[1]
        name = user_input[2]

        if not core_dict_logic.remove(line_data, dictionary_input, name):
            return

        file_modification.update(line_data)

    elif command == 'automatch':
        if wrong_parameter_count(0):
            return

        settings = line_data['settings']
        auto_match_toggle = settings['auto_match_toggle']
        if not auto_match_toggle:  # If it's off (default)
            settings['auto_match_toggle'] = True
            print('Enabled auto matching (applies to sell, expand, fee, dividend)')
        else:  # If it's on already
            settings['auto_match_toggle'] = False
            print('Disabled auto matching (applies to sell, expand, fee, dividend)')

        file_modification.update(line_data)

    elif command == 'settings':
        if wrong_parameter_count(0):
            return
        console_display.print_settings(line_data)

    elif command == 'alias':
        if wrong_parameter_count(0):
            return
        documentation.print_alias()

    elif command == 'module':
        if wrong_parameter_count(0, 1):
            return
        if input_length == 1:
            documentation.print_modules()
        elif input_length == 2:
            module_name = user_input[1]
            documentation.print_module(module_name)

    elif command == 'help':
        if wrong_parameter_count(0, 1):
            return
        if input_length == 1:
            documentation.print_help()
        else:  # input_length == 2
            command = user_input[1]
            documentation.print_help(command)

    elif command == 'reset':
        if wrong_parameter_count(0):
            return

        while True:
            print('Wipe ALL data? (y/n)')
            user_input = input().lower()
            if user_input == 'y':
                break
            elif user_input == 'n':
                return
        file_modification.create_dat()
        line_data.clear()
        line_data.update(file_modification.initialize_data())
        print('Reset all data')
        console_display.print_welcome(line_data)
        console_display.print_net(line_data)

    elif command in {'exit', 'quit', 'stop'}:
        quit('SMngr closed')

    else:
        print('Invalid command')
