import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# Ticker-Symbol eingeben
ticker = input()

# Daten der letzten 5 Jahre herunterladen
now = str(round(time.time()))
history_start = str(round(time.time()-5*365*24*60*60))
df = pd.read_csv("https://query1.finance.yahoo.com/v7/finance/download/"+ticker+"?period1="+history_start+"&period2="+now+"&interval=1d&events=history")

# Daten anpassen
df["Date"] = pd.to_datetime(df["Date"])
data = df.filter(['Date','Close'])
data.set_index("Date", inplace=True)

# 200-Tage-Linie berechnen
data['SMA200'] = data.rolling(window=200).mean()

# Diagramm anzeigen
fig = plt.figure(figsize=(12,8))
plt.title(ticker)
plt.xlabel("Datum")
plt.ylabel("Preis")
plt.plot(data.index, data["Close"], label="Schlusskurs")
plt.plot(data.index, data["SMA200"], label="SMA200")
plt.legend(loc='upper left')
plt.show()
