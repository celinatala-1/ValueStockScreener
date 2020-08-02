import os
import pandas as pd
from yahooquery import *

#the script to pull all companies listed on a exchange and cleaning it up

filename = "nasdaq.csv"
#getting the file nasdaq ftp and deleting the first few lines/last line
os.system("curl --ftp-ssl anonymous:celinahtala@gmail.com "
          "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt "
          "> nasdaq.txt")

os.system("sed -i '' -e 1,8d -e '$ d' nasdaq.txt")


columns = ["Ticker", "Old_Name", "Category", "Test", "Status"]
all_stocks = pd.read_csv("nasdaq.txt", header = None, names = columns, usecols=[0, 1, 2, 3, 4], delimiter="|")
#only keeping the rows from the Capital Market, where it is not a test issue and has normal financial status

all_stocks.drop(all_stocks.loc[(all_stocks['Category'] != "S")].index, inplace=True)
all_stocks.drop(all_stocks.loc[(all_stocks['Test'] == "Y")].index, inplace=True)
all_stocks.drop(all_stocks.loc[(all_stocks['Status'] != "N")].index, inplace=True)

#changing the name by getting rid of the - Common Stock
def changeName(name):
    return name.split("-")[0].strip()

all_stocks['Name'] = all_stocks['Old_Name'].apply(changeName)

#only keeping Ticker and Cleaned Name
all_stocks.drop(columns=["Category", "Test", "Status", "Old_Name"], inplace=True)
all_stocks.drop_duplicates(subset='Name', inplace=True, ignore_index=True)

#adding the CIK number to each stock
ticker_cik = open("ticker_CIX.txt")
t_cik = {}
for line in ticker_cik:
    x = line.split("\t")
    t_cik[x[0].upper()] = x[1].strip()

def add_cik(ticker):
    if ticker in t_cik:
        return t_cik[ticker]
all_stocks['CIK'] = all_stocks['Ticker'].apply(add_cik)

#the different criteria that this screener will have to match
criterion = ['Name', 'Ticker', 'Price', 'Sector', 'MarketCap', 'PE', 'ROE', 'ROA']
filtered_stocks = pd.DataFrame(columns=criterion)
filtered_stocks.set_index('Ticker')
extra_stocks = pd.DataFrame(columns=criterion)
extra_stocks.set_index('Ticker')

#going through all the stocks in our df
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
        else:
            extra_stocks.loc[ticker] = [name, ticker, price, sector, m_cap, pe, roe, roa]

    except:
        extra_stocks.loc[ticker] = [ticker, name, None, None, None, None, None, None]

def changeMarketCap(market):
    return "{:,}".format(market//1000000)
filtered_stocks['MarketCap'] = filtered_stocks['MarketCap'].apply(changeMarketCap)

#cleaning up the numbers 
filtered_stocks['PE'] = filtered_stocks['PE'].apply(lambda x: "{:.1f}".format(x))
filtered_stocks['ROE'] = filtered_stocks['ROE'].apply(lambda x: "{:.1f}".format(x * 100))
filtered_stocks['ROA'] = filtered_stocks['ROA'].apply(lambda x: "{:.1f}".format(x * 100))

all_stocks.to_csv(filename)
filtered_stocks.to_csv("filtered_stocks_nasdaq.csv")
extra_stocks.to_csv("other_stocks_nasdaq.csv")