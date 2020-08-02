# ValueStockScreener
Queries all stocks on both NASDAQ and NYSE and filters them based on certain financial metrics. The program will output two CSV files, one that contains the companies that meet the criteria and another that do not. I utilize the YahooQuery API to get the relevant financial metrics. 

### Requirements
* Pandas
* yahooquery

### Implementation
Simply run the fetching_data_nasdaq.py or the fetching_data_nyse.py file

### Code
Both programs follow a similar workflow
1. Pulling the list of all tickers from the `nasdaqtrader` website and saving it as a txt file
2. Cleaning the file by only pulling the relevant companies
3. Utilizing yahooQuery to pull the relevant information about these companies and populating a dataframe 
4. Saving the dataframe as a CSV file