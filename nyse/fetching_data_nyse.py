import os
import pandas as pd
import re
from yahooquery import *

#the script to pull all companies listed on a exchange and cleaning it up
#
filename = "nyse.csv"
# # getting the file nasdaq ftp and deleting the first few lines/last line
# # os.system("curl --ftp-ssl anonymous:celinahtala@gmail.com "
# #           "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt "
# #           "> nyse.txt")
# # # #
# # os.system("sed -i '' -e 1,7d -e '$ d' nyse.txt")
columns = ['Ticker', 'Name', 'Exchange', 'ETF', 'Test']

#dropping all ETF, non NYSE stocks, and test runs
all_stocks = pd.read_csv("nyse.txt", header = None, names = columns, usecols=[0, 1, 2, 4, 6], delimiter="|")
all_stocks.drop(all_stocks.loc[(all_stocks['Exchange'] != "N")].index, inplace=True)
all_stocks.drop(all_stocks.loc[(all_stocks['ETF'] == "Y")].index, inplace=True)
all_stocks.drop(all_stocks.loc[(all_stocks['Test'] == "Y")].index, inplace=True)

#making the name cleaner
pattern = ['\d', 'Depositary Shares', 'Class [A-B]', 'Common *Stock', 'Common Shares', 'Units', 'Preferred Series [A-C]', 'Series [A-C]', "Shares", 'Stocks*', "Preferred"]

for index, row in all_stocks.iterrows():
    name = row['Name']
    for p in pattern:
        m = re.search(p, name)
        if m:
            name = name[:m.start()].strip()
    row['Name'] = name

all_stocks.drop(columns=['Exchange', 'ETF', 'Test'], inplace=True)
all_stocks.drop_duplicates(subset='Name',inplace=True)
for index, row in all_stocks.iterrows():
    ticker = row['Ticker']
    if not ticker.isalpha():
        all_stocks.drop(index=index, inplace=True)

criterion = ['Name', 'Ticker', 'Price', 'Sector', 'MarketCap', 'PE', 'ROE', 'ROA']
filtered_stocks = pd.DataFrame(columns=criterion)
filtered_stocks.set_index('Ticker')
extra_stocks = pd.DataFrame(columns=['Ticker', 'Name'])
extra_stocks.set_index('Ticker')

for index, row in all_stocks.iterrows():
    ticker = row['Ticker']
    name = row['Name']
    try:
        t = Ticker(ticker)
        sector = t.summary_profile[ticker]['sector']
        m_cap = t.summary_detail[ticker]['marketCap']
        pe = t.summary_detail[ticker]['trailingPE']
        roe = t.financial_data[ticker]['returnOnEquity']
        roa = t.financial_data[ticker]['returnOnAssets']
        price = t.financial_data[ticker]['currentPrice']
        if (sector != "Financial Services" and sector != "Real Estate") \
                and (m_cap > 500000000) and (pe <= 15) and (roe >=0.15)\
                and (roa >= 0.05):
            filtered_stocks.loc[ticker] = [name, ticker, price, sector, m_cap, pe, roe, roa]
    except:
        extra_stocks.loc[ticker] = [ticker, name]

def changeMarketCap(market):
    return "{:,}".format(market//1000000)
filtered_stocks['MarketCap'] = filtered_stocks['MarketCap'].apply(changeMarketCap)

filtered_stocks['PE'] = filtered_stocks['PE'].apply(lambda x: "{:.1f}".format(x))
filtered_stocks['ROE'] = filtered_stocks['ROE'].apply(lambda x: "{:.1f}".format(x * 100))
filtered_stocks['ROA'] = filtered_stocks['ROA'].apply(lambda x: "{:.1f}".format(x * 100))

all_stocks.to_csv(filename)
filtered_stocks.to_csv("filtered_stocks_nyse.csv")
extra_stocks.to_csv("extra_stocks_nyse.csv")


