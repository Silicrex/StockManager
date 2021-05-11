import file_modification
import live_price_info


def print_welcome(line_data):
    print('Welcome! SMngr loaded')
    if line_data['start']:
        print(f"Started on {line_data['start'][0]}\n")
    else:
        print("'start' to set date")


def print_net(line_data):
    net = line_data['net']
    print('Current net: {:+.2f}'.format(net))


def print_current(line_data):
    # value = {quantity: x, cost basis: x}
    for key, value in line_data['current'].items():
        quantity = value['quantity']
        total_cost = value['bought_total']
        print(f'{key}: [{quantity}] @ {round(total_cost / quantity, 2)}')


def print_adjusted_net(line_data):
    current = line_data['current']
    net = line_data['net']
    # value = [quantity, cost basis]
    for key, value in current.items():
        quantity = value['quantity']
        try:
            live_price = round(live_price_info.get_stock_price(key), 2)
        except IndexError:
            continue
        net += quantity * live_price
    net = round(net, 2)
    print('Adjusted net: {:+.2f}'.format(net))


def print_current_prices(line_data):
    current = line_data['current']

    for key, value in current.items():
        quantity = value['quantity']
        price = round(live_price_info.get_stock_price(key), 2)
        print(f"({quantity}) {key} @ {price}")


def print_peaks(line_data):
    current = line_data['current']

    for key, value in current.items():
        quantity = value['quantity']
        low = round(live_price_info.get_stock_low(key), 2)
        high = round(live_price_info.get_stock_high(key), 2)
        print(f"({quantity}) {key} (daily peaks) @ ({low}, {high})")


def print_highs(line_data):
    current = line_data['current']

    for key, value in current.items():
        quantity = value['quantity']
        high = round(live_price_info.get_stock_high(key), 2)
        print(f"({quantity}) {key} (daily high) @ {high}")


def print_lows(line_data):
    current = line_data['current']

    for key, value in current.items():
        quantity = value['quantity']
        low = round(live_price_info.get_stock_low(key), 2)
        print(f"({quantity}) {key} (daily low) @ {low}")


def print_expanded(line_data, name, live_price, net_value):
    # 'bought_quantity', 'bought_total', 'highest_buy', 'lowest_buy', 'sold_quantity',
    # 'sold_total', 'highest_sell', 'lowest_sell', 'net_value', 'date'
    current = line_data['current']
    history = line_data['history']

    item = history[name]
    bought_quantity = item['bought_quantity']
    bought_total = item['bought_total']
    highest_buy = item['highest_buy']
    lowest_buy = item['lowest_buy']
    sold_quantity = item['sold_quantity']
    sold_total = item['sold_total']
    highest_sell = item['highest_sell']
    lowest_sell = item['lowest_sell']
    fee = item['fee']
    dividend = item['dividend']
    date = item['date']

    if name in current:  # If currently owned
        quantity = current[name]['quantity']
    else:
        quantity = 0

    print(f'- ({quantity}) {name} ', end='')  # Quantity, name
    if quantity:  # Display current price if currently owned
        print('(unsettled @ {:.2f}, basis @ {:.2f}) '.format(live_price, round(bought_total / quantity, 2)), end='')
    print('| {:+.2%}'.format(net_value))  # Print net
    print('{} bought ({:+.2f}), '.format(bought_quantity, -bought_total), end='')  # Bought #, total
    print('{} sold ({:+.2f}), '.format(sold_quantity, sold_total), end='')  # Sold #, total
    print('fee ({:+.2f}), dividend ({:+.2f})'.format(-fee, dividend))
    print('(since {}) (low, high) buy: ({:.2f}, {:.2f}), '.format(date, lowest_buy, highest_buy), end='')
    if highest_sell is None:  # If there have been none sold, print N/A
        print('sell: (N/A, N/A)')
    else:
        print('sell: ({:.2f}, {:.2f})'.format(lowest_sell, highest_sell))


def print_watchlist(line_data, mode='live'):
    watchlist = line_data['watchlist']
    remove_list = []  # If symbols error, queue them to be removed

    if not watchlist:  # If watchlist is empty
        print('Watchlist is empty')
        return

    # Two modes: print live price, or print day low/high
    if mode == 'live':  # Live price mode
        for key in watchlist:
            try:
                value = round(live_price_info.get_stock_price(key), 2)
            except IndexError:
                print('Removing from list')
                remove_list.append(key)
                continue
            print(key, '@ {:.2f}'.format(value))
    elif mode == 'peaks':
        for key in watchlist:
            try:
                low = round(live_price_info.get_stock_low(key), 2)
                high = round(live_price_info.get_stock_high(key), 2)
            except IndexError:
                print('Removing from list')
                remove_list.append(key)
                continue
            print(key, '@ ({:.2f}, {:.2f})'.format(low, high))

    for key in remove_list:
        watchlist.remove(key)
    file_modification.update(line_data)


def print_settings(line_data):
    for setting, value in line_data['settings'].items():
        print(f'{setting}: {value}')
