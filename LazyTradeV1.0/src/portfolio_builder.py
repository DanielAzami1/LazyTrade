import wikipedia
from yahoo_fin import stock_info as si
import sqlite3
import random
import os
import stockscraper
import subprocess as sp
import copy

def get_updated_prices(portfolio : dict) -> float:
    """Takes in a portfolio as arg and returns a value indicating the portfolio's
    current value, while also appending the price changes of individual assets to the
    original dict."""
    new_portfolio_value = 0
    for lst in portfolio["stocks"]:
        new_price = int(si.get_live_price(lst[1]))
        new_portfolio_value += new_price * lst[3]
        change = ((new_price - lst[2]) / lst[2]) * 100
        if change > 0:
            lst.append("+" + str(round(change,2)) + "%")
        else:
            lst.append(str(round(change, 2)) + "%")
    return new_portfolio_value
    
def get_old_portfolio_value(portfolio : dict) -> float:
    """Retrieves the portfolio value at the time of creation"""
    portfolio_value = 0
    for lst in portfolio["stocks"]:
        portfolio_value += (lst[2] * lst[3])
    return portfolio_value

        
def print_portfolio(portfolio : dict) -> None:
    """Prints the portfolio (stored as a dict) passed in as argument."""
    new_portfolio_value = round(get_updated_prices(portfolio), 2)
    old_portfolio_value = get_old_portfolio_value(portfolio)
    portfolio_change = ((new_portfolio_value - old_portfolio_value) / old_portfolio_value) * 100
    if portfolio_change > 0:
        portfolio_change = "+" + str(round(portfolio_change, 2)) + "%"
    else:
        portfolio_change = str(round(portfolio_change, 2)) + "%"
        
    print("\nPortfolio Overview:\n"
                + "--------------------------------------\n"
                + "\tName : " + portfolio["name"] + " \n"
                + "\tValue : $" + str(new_portfolio_value) + " (" + portfolio_change + ") \n"
                + "\t# of unique stocks : " + str(portfolio["num_stocks"]))
    print("\tStocklist :")
    for lst in portfolio["stocks"]:
        lst = [str(item) for item in lst]
        print(f"\t\t-{lst[0]} ({lst[1]}), ${lst[2]}, {lst[3]} shares | ({lst[4]})")
    print("--------------------------------------\n")

def save_new_to_db(portfolio : dict) -> None:
    """Inserts stock data into an sqlite3 db from a newly constructed portfolio passed as a dict, removes existing table if the name
    Corresponds to an already stored portfollio"""
    portfolio_name = portfolio["name"]
    if os.path.exists(f".\\data\\{portfolio_name}.db"):
        os.remove(f".\\data\\{portfolio_name}.db")
    conn = sqlite3.connect(".\\data\\" + portfolio_name + ".db")
    c = conn.cursor()
    c.execute('''CREATE TABLE portfolio
                (stock text, ticker text, price real, shares integer)''')
    for lst in portfolio["stocks"]:
        c.execute("INSERT INTO portfolio VALUES (?,?,?,?)", lst[:4])
        conn.commit()
    conn.close()
    print(f"\n\t-> Saved portfolio '{portfolio_name}'.")

def save_to_db(portfolio : dict) -> None:
    """Updates stock data into an sqlite3 db from existing portfolio passed as a dict"""
    portfolio_name = portfolio["name"]
    conn = sqlite3.connect(".\\data\\" + portfolio_name + ".db")
    c = conn.cursor()
    for lst in portfolio["stocks"]:
        c.execute("INSERT INTO portfolio VALUES (?,?,?,?)", lst[:4])
        conn.commit()
    conn.close()
    print(f"\n\t-> Saved changes to '{portfolio_name}'.")

def remove_from_db(stock_ticker : str, portfolio_name : str) -> None:
    conn = sqlite3.connect(".\\data\\" + portfolio_name + ".db")
    c = conn.cursor()
    c.execute("DELETE FROM portfolio WHERE ticker = ?" , (stock_ticker,))
    conn.commit()
    conn.close()

def load_from_db(portfolio_name : str, portfolio : dict) -> dict:
    """Retrieves stock data from local sqlite3 db and appends it to the dict passed in as arg"""
    tmp = sp.call("cls", shell=True)
    print(f"\n\t-> Loading {portfolio_name} from memory...\n") 
    conn = sqlite3.connect(".\\data\\" + portfolio_name + ".db")
    c = conn.cursor()
    for row in c.execute("SELECT * FROM portfolio"):
        portfolio["stocks"].append(list(row))
    portfolio["num_stocks"] = len(portfolio["stocks"])
    return portfolio

    

def load_or_build() -> dict:
    """Takes in user input to determine whether to query a local db to load portfolio, or call
    build new portfolio function to generate a new portfolio - either way, a portfolio (dict) is
    returned"""
    portfolio = {"name" : "",
                 "stocks" : [],
                 "num_stocks" : 0}
    while True:
        load_build = input("\nEnter:"
              + "\n\t1. To load an existing portfolio from memory"
              + "\n\t2. To create a new portfolio\n")
        if load_build == "1":
            stored_portfolios = [file for file in os.listdir(".\\data\\") if os.path.isfile(os.path.join(".\\data\\", file))]
            if not stored_portfolios:
                print("\n\t-> Could not find any portfolios in .\\data\\")
                continue
            else:
                print("\n\t-> Located the following portfolios:\n")
                for index, file in enumerate(stored_portfolios):
                    if file.endswith(".db"):
                        print((f"\t\t{index+1} : {file}\n")[:-4])
                while True:
                    try:
                        selected_portfolio = input("\nEnter number for portfolio you wish to load: ")
                        selected_portfolio = int(selected_portfolio)
                        if selected_portfolio <= 0 or selected_portfolio > index+1:
                            raise ValueError
                        else:
                            break
                    except(TypeError, ValueError):
                        print(f"\n\t-> Invalid choice '{selected_portfolio}'.")
                        continue
                    
                portfolio = {"name" : stored_portfolios[selected_portfolio-1][:-3],
                             "stocks" : [],
                             "num_stocks" : 0}
            
                portfolio = load_from_db(portfolio["name"], portfolio) 
                break
            
        elif load_build == "2":
            while True:
                name = input("Please enter a name for your portfolio: ")
                if os.path.isfile(".\\data\\" + portfolio["name"] + ".db"):
                    print(f"\n\t-> Portfolio {name} already exists.\n")
                else:
                    break
            portfolio["name"] = name
            portfolio = build_portfolio(portfolio)
            break
        else:
            print (f"\n\t-> Invalid choice '{load_build}'.")
    return portfolio

    

    
def build_portfolio(portfolio : dict) -> dict:
    """Loads stockscraper module to scrape stocklist from snp500 wiki page. Continually reccomends stocks
    and gives the user an option to append the stock data to the dict passed in as arg. Exits after (potentially)
    calling save_to_db method and returns the newly constructed dict"""
    default = copy.deepcopy(portfolio)
    new_portfolio = False
    if portfolio["num_stocks"] == 0:
        new_portfolio = True
    stop_building = False
    
    print("\n\t-> Loading stocklist from S&P500 Index...")
    stocklist = stockscraper.get_stocklist_snp()
    print("\t\t\t\t-> Done!\n")
    
    stocks_out = 0
    while not stop_building:
        tmp = sp.call("cls", shell=True)
        stocks_out += 1
        print("LazyTrade")
        print(f"---------------------------------------{stocks_out}---------------------------------------")
        stock, ticker = random.choice(list(stocklist.items()))
        if stock in portfolio.keys():
            continue
        print(f"Asset : {stock} | Ticker : {ticker}")
        current_price = str(round(si.get_live_price(ticker), 2))
        print("Current price : $" + current_price)
        try:
            print("Summary : " + wikipedia.summary(stock, sentences=2))
        except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError):
            print("\n\t-> [Summary could not be loaded]")
            
        print(f"---------------------------------------{stocks_out}---------------------------------------")
        while True:
            choice = input(f"\nAdd {stock} to your portfolio? (y/n, 'info' for additional information, or 'stop' to stop adding stocks).\n").lower() 
            if choice == "info" or choice == "i":
                quote_table = si.get_quote_table(ticker)
                print(f"===================={stock}====================")
                try:
                    print("1y Target Est : $" + str(quote_table["1y Target Est"])
                          + "\n52 Week Range : $(" + str(quote_table["52 Week Range"]) + ")"
                          + "\nBeta (5Y Monthly) : " + str(quote_table["Beta (5Y Monthly)"])
                          + "\nEarnings Date : " + str(quote_table["Earnings Date"])
                          + "\nEPS (TTM) : " + str(quote_table["EPS (TTM)"])
                          + "\nMarket Cap : $" + str(quote_table["Market Cap"])
                          + "\nPE Ratio (TTM) : " + str(quote_table["PE Ratio (TTM)"])
                          + "\nVolume : " + str(quote_table["Volume"]))
                except AssertionError:
                    print("\n\t-> There was a problem loading additional information.\n")
                print(f"===================={stock}====================")
            elif choice == "y" or choice == "yes":
                while True:
                    try:
                        num_of_shares = int(input(f"Enter number of shares of {stock} you would like to purchase:\n"))
                        if num_of_shares <= 0:
                            raise ValueError
                        break
                    except (TypeError, ValueError):
                        print(f"\n\t-> Invalid shares amount '{num_of_shares}'.\n") 
                    
                #print(f"\n\t-> Successfully added {num_of_shares} shares of {stock} to your portfolio!\n")
                portfolio["stocks"].append([stock, ticker, float(current_price), num_of_shares])
                portfolio["num_stocks"] = len(portfolio["stocks"])
                break
            elif choice == "n" or choice == "no":
                print(f"\n\t-> Stock {stock} was rejected.\n")
                break
            elif choice == "s" or choice == "stop":
                print("\n\t-> Finishing portfolio construction.")
                #print_portfolio(portfolio)
                save_portfolio = input("\nSave changes to portfolio " + portfolio["name"] + "?\n").lower()
                if save_portfolio in "yes ok":
                    if new_portfolio:
                        save_new_to_db(portfolio)
                    else:
                        save_to_db(portfolio)
                else:
                    print("\n\t-> Portfolio has not been saved.\n")
                    return default
                stop_building = True
                break
            else:
                print(f"\n\t-> Invalid choice '{choice}'.\n")
                continue
    return portfolio
