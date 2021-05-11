import datetime


def get_template_dict():
    template_dict = {
        'start': 'None',
        'net': 0,
        'current': {},  # {name: {quantity, bought_total}} ex {cake: {quantity: 1, bought_total: 110}}
        'history': {},  # {name: {bought_quantity, bought_total, highest_buy, lowest_buy, sold_quantity,
                        #  sold_total, highest_sell, lowest_sell, fee, dividend, date}}
        'watchlist': [],
        'settings': {'auto_match_toggle': False},
    }
    return template_dict


def buy(line_data, name, quantity, cost, date=None):
    def create_current():
        current[name] = {'quantity': quantity, 'bought_total': bought_total}

    def create_history():
        nonlocal date
        if date is None:
            date = str(datetime.date.today())
        history[name] = {'bought_quantity': quantity, 'bought_total': bought_total, 'highest_buy': cost,
                         'lowest_buy': cost, 'sold_quantity': 0, 'sold_total': 0, 'highest_sell': None,
                         'lowest_sell': None, 'fee': 0, 'dividend': 0, 'date': date}

    def increment_current():
        update_current(line_data, name, 'quantity', quantity)
        update_current(line_data, name, 'bought_total', bought_total)

    def increment_history():
        update_history(line_data, name, 'bought_quantity', quantity)
        update_history(line_data, name, 'bought_total', bought_total)

        if cost > history[name]['highest_buy']:
            history[name]['highest_buy'] = cost
        elif cost < history[name]['lowest_buy']:
            history[name]['lowest_buy'] = cost

    if quantity <= 0:
        print('Cannot be <= 0')
        return False

    current = line_data['current']
    history = line_data['history']
    bought_total = round(cost * quantity, 2)

    if name in current:  # If already in current, definitely in history too
        increment_current()
        increment_history()
    elif name in history:  # Not in current but in history already
        create_current()
        increment_history()
    else:  # Not in current or history
        create_current()
        create_history()

    line_data['net'] = round(line_data['net'] - bought_total, 2)
    return True


def sell(line_data, name, quantity, cost):
    def increment_history():
        update_history(line_data, name, 'sold_quantity', quantity)
        update_history(line_data, name, 'sold_total', total_sell_cost)

        highest_sell = item_value['highest_sell']
        lowest_sell = item_value['lowest_sell']

        if highest_sell is None:
            item_value['highest_sell'] = cost
            item_value['lowest_sell'] = cost
        elif cost > highest_sell:
            item_value['highest_sell'] = cost
        elif cost < lowest_sell:
            item_value['lowest_sell'] = cost

    current = line_data['current']

    if name not in current:
        if not (name := item_search(name, current, line_data['settings']['auto_match_toggle'])):
            return False

    item_value = line_data['history'][name]
    total_sell_cost = round(cost * quantity, 2)

    total_buy_cost = current[name]['bought_total']
    total_quantity = current[name]['quantity']
    buy_avg = total_buy_cost / total_quantity

    if quantity > current[name]['quantity']:
        print('Cannot sell more than you have')
        return False

    update_current(line_data, name, 'quantity', -quantity)
    # Reduce left total by proportion of avg
    current[name][1] = round(total_buy_cost * (1 - quantity / total_quantity), 2)

    increment_history()

    line_data['net'] = round(line_data['net'] + total_sell_cost, 2)

    if current[name]['quantity'] == 0:
        current.pop(name)

    print('Cost basis: {:.2f}, sold @ {:.2f} ({:+.2f})'.format(buy_avg, cost, cost - buy_avg))
    return True


def fee_item(line_data, name, fee):
    history = line_data['history']
    if name not in history:
        if not (name := item_search(name, history, line_data['settings']['auto_match_toggle'])):
            return False

    line_data['net'] = round(line_data['net'] - fee, 2)
    update_history(line_data, name, 'fee', fee)
    return True


def dividend_item(line_data, name, dividend):
    history = line_data['history']
    if name not in history:
        if not (name := item_search(name, history, line_data['settings']['auto_match_toggle'])):
            return False

    line_data['net'] = round(line_data['net'] + dividend, 2)
    update_history(line_data, name, 'dividend', dividend)
    return True


def remove(line_data, dictionary_input, name):
    if dictionary_input == 'current':
        dictionary = line_data['current']
    elif dictionary_input == 'history':
        dictionary = line_data['history']
    else:
        print('Invalid dictionary')
        return False

    if name not in dictionary:
        print('Item not found')
        return False

    dictionary.pop(name)
    print('Item removed')
    return True


def update_current(line_data, name, index, value):  # Handles float rounding
    item_value = line_data['current'][name]
    current_value = item_value[index]
    item_value[index] = round(current_value + value, 2)


def update_history(line_data, name, index, value):
    item_value = line_data['history'][name]
    current_value = item_value[index]
    item_value[index] = round(current_value + value, 2)


def calculate_history_net(line_data, name, live_price=0):
    current = line_data['current']
    history = line_data['history']

    if name not in history:  # If none have been owned, raise an exception
        raise IndexError("Item not in history dict")

    item_value = history[name]
    bought_total = item_value['bought_total']
    sold_total = item_value['sold_total']
    fee = item_value['fee']
    dividend = item_value['dividend']

    unsettled_total = 0  # Only affected if item is currently owned

    if bought_total != 0:  # Don't divide by 0, just set net to 0 if you've only gotten this item for free
        if name in current:  # If currently owned; get unsettled cost total based on live price
            quantity = current[name]['quantity']
            unsettled_total = round(quantity * live_price, 2)

        # -1 to make it difference (+50% not *150%), 4 because it's a % and we want 2 decimal points (0.5624 = 56.24%)
        net = round((sold_total + unsettled_total + dividend - fee) / bought_total - 1, 4)
    else:
        net = 0
    return net


def sort_current(line_data):
    temp_list = list(line_data['current'].items())
    temp_list = sorted(temp_list, key=lambda obj: (-obj[1]['quantity'], obj[0]))  # (quantity, name)
    line_data['current'] = dict(temp_list)


# def sort_history(line_data):
#     temp_list = list(line_data['history'].items())
#     temp_list = sorted(temp_list, key=lambda obj: (-obj[1]['net_value'], obj[0]))  # (net_value, name)
#     line_data['history'] = dict(temp_list)


def watchlist_add(line_data, name):
    watchlist = line_data['watchlist']
    if name in watchlist:
        print('Item is already on watchlist')
        return False
    watchlist.append(name)
    return True


def watchlist_remove(line_data, name):
    watchlist = line_data['watchlist']
    if name not in watchlist:
        print('Item is not on watchlist')
        return False
    watchlist.remove(name)
    return True


def validate_date(date):
    # Year-Month-Day
    first_hyphen = date.find('-')
    if first_hyphen == -1:
        return False

    second_hyphen = date.find('-', first_hyphen + 1)
    if second_hyphen == -1:
        return False

    year = date[:first_hyphen].lstrip('0')
    if not year.isdigit():
        return False

    month = date[first_hyphen + 1:second_hyphen]
    if not month.isdigit():
        return False
    if len(month) == 1:
        month = '0' + month

    day = date[second_hyphen + 1:]
    if not day.isdigit():
        return False
    if len(day) == 1:
        day = '0' + day

    if not valid_date(int(month), int(day)):
        return False

    return year + '-' + month + '-' + day


def valid_date(month, day):
    # Given month 1-12, day 1-31
    if month in {1, 3, 5, 7, 8, 10, 12}:  # 31
        return True  # We already know day is in the range [1, 31]
    elif month in {4, 6, 9, 11}:  # 30
        if day < 31:
            return True
    elif month == 2:  # 28/29
        if day < 30:
            return True
    return False


def item_search(invalid_item, dictionary, auto_match_toggle):
    for item in dictionary:
        if item.startswith(invalid_item):
            if auto_match_toggle:
                print(f"Auto-matched '{invalid_item}' to '{item}' (you can disable this with 'automatch')")
                return item
            print(f'Did not find {invalid_item}, but found {item}. Use this? (y/n/cancel)')
            while True:
                user_input = input().lower()
                if user_input in {'yes', 'y'}:
                    return item
                elif user_input in {'no', 'n'}:
                    break
                elif user_input in {'cancel', 'c'}:
                    print('Returning to menu')
                    return False
    print("You don't have any of those")
    return False
