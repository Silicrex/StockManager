import console_display
import core_dict_logic
import live_price_info


def print_history(line_data):
    def print_page():
        print(f'Page {page}/{total_pages}:')

        # Get min between keys_per_page and # of keys left from index (so last page doesn't index error)
        for n in range(min(keys_per_page, keys_length - (page - 1) * keys_per_page)):
            print()  # Newline
            # Offset index to that page
            index = (page - 1) * keys_per_page + n
            console_display.print_expanded(line_data, item_list[index][0], item_list[index][1], item_list[index][2])

    history = line_data['history']

    # Create and fill item_list, to provide print_expanded its info
    item_list = [[x, 0, 0] for x in history]  # 3-element list of [key, 0, 0] (placeholders for live price and net)
    # [item name, live price, net value]
    for value in item_list:
        item_name = value[0]
        try:
            live_price = round(live_price_info.get_stock_price(item_name), 2)
        except IndexError:
            return
        value[1] = live_price
        value[2] = core_dict_logic.calculate_history_net(line_data, item_name, live_price)
    item_list = sorted_item_list(item_list)

    keys = list(history)
    keys_length = len(keys)

    page = 1  # Default value
    keys_per_page = 4  # Configurable
    total_pages = key_to_page(keys_length, keys_per_page)

    print(f"Entering history interface ({keys_length} items). Say 'exit' to return to menu, or 'help' for help")
    print_page()
    print()  # Newline to separate input from print

    while True:
        user_input = input().lower().split()
        input_length = len(user_input)
        command = user_input[0]
        print()  # Newline to separate input from print

        if input_length > 2:
            print('Invalid amount of parameters for history interface')
            continue

        if command in {'next', 'n'}:
            pages_to_next = 1
            if input_length == 2:  # Specific value given
                try:
                    pages_to_next = int(eval(user_input[1]))
                except (NameError, SyntaxError, TypeError):
                    print('Invalid command usage for history interface')
                    continue
            page += pages_to_next
            if page > total_pages:
                page = total_pages
            print_page()

        elif command in {'previous', 'p'}:
            pages_to_previous = 1
            if input_length == 2:  # Specific value given
                try:
                    pages_to_previous = int(eval(user_input[1]))
                except (NameError, SyntaxError, TypeError):
                    print('Invalid command usage for history interface')
                    continue
            page -= pages_to_previous
            if page < 1:
                page = 1
            print_page()

        elif command in {'page', 'pg'} and input_length == 2:
            item_name = user_input[1]
            try:
                item_index = keys.index(item_name)
            except ValueError:
                print('Item not found')
                continue
            page = key_to_page(item_index + 1, keys_per_page)
            print_page()

        elif command in {'refresh', 'r'}:
            # [item name, live price, net value]
            for value in item_list:
                item_name = value[0]
                try:
                    live_price = round(live_price_info.get_stock_price(item_name), 2)
                except IndexError:
                    return
                value[1] = live_price
                value[2] = core_dict_logic.calculate_history_net(line_data, item_name, live_price)
            item_list = sorted_item_list(item_list)
            print('Prices refreshed')
            print_page()

        elif command == 'help':
            print_history_commands()

        elif command in {'exit', 'e'}:
            print('Returning to menu')
            return

        elif input_length == 1:  # Check for page number syntax
            try:
                page = int(eval(command))
            except (NameError, SyntaxError, TypeError):
                print('Invalid command usage for history interface')
                continue

            if page > total_pages:
                page = total_pages
            elif page < 1:
                page = 1
            print_page()

        else:
            print('Invalid command usage for history interface')
        print()  # Newline to separate input from print


def key_to_page(key_count, keys_per_page):
    return round(1 + (key_count - 1) // keys_per_page)  # 0 = 0 page, 1-20 = 1 page, 21-40 = 2 pages w/ 20


def sorted_item_list(item_list):
    return sorted(item_list, key=lambda val: (-val[2], val[0]))  # (net_value, name)


def print_history_commands():
    print("\n'next', 'previous', 'page <item name>', '<page#>', 'refresh', 'help', 'exit'\n"
          "Aliases: 'n', 'p'\n"
          "Notes:\n"
          "- Can also give a number with next/previous\n"
          "- page <item name> navigates to page with that item\n"
          "- <page#> means just the number\n"
          "- Refresh updates prices (unsettled # is live price)\n")
