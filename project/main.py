from pandas.plotting import register_matplotlib_converters
from Stock import Stock
from StockCollection import StockCollection

register_matplotlib_converters()

stocks = StockCollection()
start_date = '2005-01-01'

tickers = []
while True:
    print("Ticker Symbol:")
    ticker = input("> ")
    if ticker == "":
        if stocks.count() >= 1:
            break
        else:
            continue
    print("Name for \"" + ticker + "\":")
    name = input("> ")
    if name == "":
        name = ticker
    stocks.add_stock(Stock(ticker, start_date, name=name))
    print("\"" + name + "\" has been added\n\n")

selected_option = "_"


def get_options_from_user_input():
    print("----------------------------------------------------------------------------------------------------")
    print("[1] Correlation\n"
          "[2] 200-Day-Line\n"
          "[3] Ichimoku-Chart")
    return input("> ")


while True:
    selected_option = get_options_from_user_input()
    if selected_option == "1":
        stocks.get_correlation()
    elif selected_option == "2":
        stocks.show_stock_list()

        index = int(input("> "))
        if index == 0:
            stocks.show_all_sma_charts(200)
        elif 0 < index <= stocks.count():
            stocks.get_stock(index-1).show_sma_chart(200)
    elif selected_option == "3":
        stocks.show_stock_list()

        index = int(input("> "))
        if index == 0:
            stocks.show_all_ichimoku_charts()
        elif 1 <= index <= stocks.count():
            stocks.get_stock(index - 1).show_ichimoku_chart()
    elif selected_option.lower() == "x" or selected_option.lower() == "exit":
        break
