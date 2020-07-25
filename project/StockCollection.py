import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class StockCollection(object):
    def __init__(self):
        self.__stocks = []

    def add_stock(self, stock):
        self.__stocks.append(stock)

    def get_stock(self, index):
        return self.__stocks[index]

    def get_stocks(self):
        return self.__stocks

    def count(self):
        return len(self.__stocks)

    def get_correlation(self):
        all_stocks = self.__stocks[0].get_historical_close()
        tickers = [self.__stocks[0].get_name()]
        for stock in self.__stocks[1:]:
            all_stocks = pd.merge(all_stocks,
                                  stock.get_historical_close(),
                                  left_index=True,
                                  right_index=True)
            tickers.append(stock.get_name())

        all_stocks.columns = tickers
        corr = all_stocks.corr()
        plt.imshow(corr, cmap='hot', interpolation='nearest')
        sns.heatmap(
            corr,
            xticklabels=corr.columns,
            yticklabels=corr.columns,
            annot=True,
            center=0,
            cmap=sns.diverging_palette(150, 10, as_cmap=True)
        )
        plt.show()

    def show_stock_list(self):
        print("[0] All")
        for i in range(len(self.__stocks)):
            print("[" + str(i + 1) + "] " + self.__stocks[i].get_name())

    def show_all_sma_charts(self, days):
        for i in range(self.count()):
            self.__stocks[i-1].show_sma_chart(days)

    def show_all_ichimoku_charts(self):
        for i in range(len(self.__stocks)):
            self.__stocks[i].show_ichimoku_chart()
