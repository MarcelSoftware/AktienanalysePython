import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas_datareader import data
import datetime as dt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()


class Stock(object):
    def __init__(self, ticker, start, name=""):
        self.ticker = ticker
        self.start = start
        self.name = name
        self.df = None

        self.download()

    def download(self):
        ticker = self.ticker
        end_date = dt.date.today().strftime("%Y-%m-%d")
        self.df = data.DataReader(ticker, 'yahoo', self.start, end_date)
        return self

    def get_ticker(self):
        return self.ticker

    def get_name(self):
        if self.name == "":
            return self.ticker
        else:
            return self.name

    def get_dates(self):
        return self.df.index

    def get_historical_data(self):
        return self.df

    def get_historical_close(self):
        return self.get_historical_data().filter(["Close"])

    def get_sma(self, days):
        df_sma = self.df.copy()
        df_sma["SMA"] = df_sma["Close"].rolling(window=days).mean()
        return df_sma.filter(["SMA"])

    def show_sma_chart(self, days):
        plt.plot(self.df.index, self.df.Close)
        plt.plot(self.df.index, self.get_sma(days))
        plt.show()

    def get_ichimoku_data(self):
        days = 365 * 5
        ichmoku_data = self.df.copy()[-(days + 52):]
        ichmoku_data = ichmoku_data.reset_index()
        ichmoku_data = ichmoku_data.append(
            pd.DataFrame(
                {'Date': pd.date_range(start=ichmoku_data["Date"].iloc[-1], periods=52, freq='D', closed='right')}),
            sort=True)
        ichmoku_data["Chikō"] = ichmoku_data["Close"].shift(-26)
        ichmoku_data["Tenkan-sen"] = (ichmoku_data["Close"].rolling(window=9).max() + ichmoku_data["Close"].rolling(
            window=9).min()) / 2
        ichmoku_data["Kijun-sen"] = (ichmoku_data["Close"].rolling(window=26).max() + ichmoku_data["Close"].rolling(
            window=26).min()) / 2
        ichmoku_data["Senkō Span A"] = (ichmoku_data["Tenkan-sen"].shift(26) + ichmoku_data["Kijun-sen"].shift(26)) / 2
        ichmoku_data["Senkō Span B"] = (ichmoku_data["Close"].shift(26).rolling(window=52).max() + ichmoku_data[
            "Close"].shift(26).rolling(
            window=52).min()) / 2
        ichmoku_data = ichmoku_data.set_index("Date")
        return ichmoku_data[52:]

    def show_ichimoku_chart(self):
        print("  Buy-signal: red line crosses blue line from bottom to top (strong buy-signal when above cloud) \n \
         Sell-signal: red line crosses blue line from above to below (strong sell-signal when below cloud)\n \
         Thin cloud: Weak support / resistance zone\n \
         Thick cloud: strong support / resistance zone\n \
         Orange line above current price: Bullish market\n \
         The closer the red and blue lines are to each other, the stronger the trend")
        ichimoku_data = self.get_ichimoku_data()
        fig, ax = plt.subplots(figsize=(17, 10))

        # Draw Buy/Sell signals
        for date, order_type, price in self.get_ichimoku_signals():
            if order_type == "Buy":
                ax.axvline(x=date, color='green')
            elif order_type == "Sell":
                ax.axvline(x=date, color='red')

            plt.text(date, 0, date, rotation=90)

        # Draw all ichimoku lines
        plt.plot(ichimoku_data.index, ichimoku_data.Close, label="Kurs", color="black")
        ax.plot(ichimoku_data.index, ichimoku_data["Tenkan-sen"], color="red")
        ax.plot(ichimoku_data.index, ichimoku_data["Kijun-sen"], color="blue")
        ax.plot(ichimoku_data.index, ichimoku_data["Chikō"], color="orange")
        ax.plot(ichimoku_data.index, ichimoku_data["Senkō Span A"], 'r-', alpha=0.1)
        ax.plot(ichimoku_data.index, ichimoku_data["Senkō Span B"], 'r-', alpha=0.1)

        # Draw Green and Red clouds
        ax.fill_between(ichimoku_data.index, ichimoku_data["Senkō Span A"], ichimoku_data["Senkō Span B"],
                        where=ichimoku_data["Senkō Span B"] >= ichimoku_data["Senkō Span A"], facecolor='red',
                        interpolate=True)
        ax.fill_between(ichimoku_data.index, ichimoku_data["Senkō Span A"], ichimoku_data["Senkō Span B"],
                        where=ichimoku_data["Senkō Span B"] <= ichimoku_data["Senkō Span A"], facecolor='green',
                        interpolate=True)

        ax.legend()
        ax.set_title(self.get_name())

        plt.show()

    def get_ichimoku_signals(self):
        stock_data = self.get_ichimoku_data()
        stock_data = stock_data.filter(["Tenkan-sen", "Kijun-sen", "Close"]).dropna()
        stock_data["BuyHoldSell"] = self.get_order_types(stock_data)

        stock_data = stock_data.reset_index()
        stock_prices = []
        for index, row in stock_data.iterrows():
            stock_prices.append([row.Date, row.BuyHoldSell, row.Close])

        buy_sell = []
        for i in range(len(stock_prices)):
            if stock_prices[i][1] in ["Buy", "Sell"]:
                buy_sell.append([stock_prices[i + 1][0], stock_prices[i][1], stock_prices[i][2]])
        return buy_sell

    def get_order_type(self, sto):
        if sto["Tenkan-sen"].shift(-1) > sto["Kijun-sen"].shift(-1) & sto["Tenkan-sen"] <= sto["Kijun-sen"]:
            return "Buy"
        elif sto["Tenkan-sen"].shift(-1) < sto["Kijun-sen"].shift(-1) & sto["Tenkan-sen"] >= sto["Kijun-sen"]:
            return "Sell"
        else:
            return "Hold"

    def get_order_types(self, stock_data):
        return np.where(
            self.is_ichimoku_buy_signal(stock_data), "Buy",
            (np.where(self.is_ichimoku_sell_signal(stock_data), "Sell",
            "Hold")))

    def is_ichimoku_buy_signal(self, stock_data):
        return (stock_data["Tenkan-sen"].shift(-1) > stock_data["Kijun-sen"].shift(-1)) & (stock_data["Tenkan-sen"] <= stock_data["Kijun-sen"])

    def is_ichimoku_sell_signal(self, stock_data):
        return (stock_data["Tenkan-sen"].shift(-1) < stock_data["Kijun-sen"].shift(-1)) & (stock_data["Tenkan-sen"] >= stock_data["Kijun-sen"])
