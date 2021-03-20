import wikipedia
from yahoo_fin import stock_info as si
import sqlite3
import random
import os
import stockscraper
import portfolio_builder
import subprocess as sp

             
def main():
    print("Hello")
    tmp = sp.call("cls", shell=True)
    
    if not os.path.exists(".\\data"):
        os.makedirs(".\\data")

    print("LazyTrade v1.0\n--------------")
    
    portfolio = portfolio_builder.load_or_build()
    
    application_quit = False

    tmp = sp.call("cls", shell=True)
    
    while not application_quit:

        print("\nLazyTrade v1.0\n--------------")

        print("\n\t-> Current working portfolio: " + portfolio["name"])
        
        print("\nChoices:" 
              + "\n\t1. Add stocks to your portolio" 
              + "\n\t2. Review portfolio"
              + "\n\t3. Remove stocks from portfolio"
              + "\n\t4. Change current working portfolio"
              + "\n\t5. Quit application\n")

        try:
            choice = int(input("Select option:\n"))
        except (ValueError, TypeError):
            print(f"\n\t-> Invalid choice '{choice}'.\n")
            continue
        
        if choice == 1:
            tmp = sp.call("cls", shell=True)
            portfolio = portfolio_builder.build_portfolio(portfolio)

        elif choice == 2:
            tmp = sp.call("cls", shell=True)
            if portfolio["num_stocks"] < 1:
                print("\n\t-> Your portfolio is currently empty. Press '1' to add additional stocks.\n")
            else:
                portfolio_builder.print_portfolio(portfolio)

        elif choice == 3:
            if portfolio["num_stocks"] < 1:
                tmp = sp.call("cls", shell=True)
                print("\n\t-> Your portfolio is currently empty. Press '1' to add additional stocks.\n")
                continue
            
            stock_to_remove = input("\nEnter the ticker of the stock you want to remove from your portfolio:\n").upper()
            stock_found = False
            for lst in portfolio["stocks"]:
                if stock_to_remove in lst:
                    portfolio["stocks"].remove(lst)
                    portfolio["num_stocks"] -= 1
                    tmp = sp.call("cls", shell=True)
                    print(f"\n\t-> Stock with ticker '{stock_to_remove}' removed from current working portfolio.\n")
                    portfolio_builder.remove_from_db(stock_to_remove, portfolio["name"])
                    stock_found = True
                    break
            if not stock_found:
                tmp = sp.call("cls", shell=True)
                print(f"\n\t-> Could not locate a stock with ticker '{stock_to_remove}' in current working portolio.\n")
        
        elif choice == 4:
            tmp = sp.call("cls", shell=True)
            portfolio = portfolio_builder.load_or_build()
           
        elif choice == 5:
            tmp = sp.call("cls", shell=True)
            print("\n\t-> Application quit.\n")
            application_quit = True
        else:
            tmp = sp.call("cls", shell=True)
            print(f"\n\t-> Invalid choice '{choice}'.")

    print("\n\tGoodbye...")
    return 0

if __name__ == "__main__":
    main()
