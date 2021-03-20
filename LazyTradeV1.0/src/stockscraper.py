import requests
from bs4 import BeautifulSoup


def get_stocklist_snp():
    
    '''Returns a dictionary containing a list of stocks scraped from Wikipedia's SNP500 index
    constitutents list. The dictionary key-value pairs are stored for simplicity as
    {asset name : ticker}'''
    
    URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    page = requests.get(URL).text
    soup = BeautifulSoup(page, features="lxml")
    stocklist = {}
    stock_table = soup.find("table", id="constituents")
    stock_table_data = stock_table.tbody.find_all("tr")
    for row in stock_table_data:    
        cells = row.find_all('a')
        stocklist[cells[1].find(text=True)] = cells[0].find(text=True)
    stocklist.pop("SEC filings")
    return stocklist

def get_stocklist_dow():
    pass

