import yfinance


def get_stock_price(name):
    ticker = yfinance.Ticker(name)
    today_data = ticker.history(period='1d')
    return today_data['Close'][0]


def get_stock_high(name):
    ticker = yfinance.Ticker(name)
    today_data = ticker.history(period='1d')
    return today_data['High'][0]


def get_stock_low(name):
    ticker = yfinance.Ticker(name)
    today_data = ticker.history(period='1d')
    return today_data['Low'][0]
