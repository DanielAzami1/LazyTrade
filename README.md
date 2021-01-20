# LazyTrade

Portfolio construction tool written in Python. Utilizes various web-scraping and financial packages to sequentially 'recommend' assets, which may in-turn be added to an arbitrary 'portfolio' saved in local memory. These portfolios are persistent, and the gain/loss - both at the individual asset and overall portfolio level - are immediately available.

### Required Packages:

- *Wikipedia*   `pip install wikepdia`
- *Yahoo_finance*   `pip install yahoo_finance`
- *BeautifulSoup*   `pip install beautifulsoup4`
---

## V1.0
- [x] Basic CLI interface, navigable to achieve essential functionality
- [x] Consistent input validation across all operations
- [x] Portfolios may be stored, and modified as neccessary (add/remove assets)
- [x] Performance is tracked at a basic level (gain/loss%)
- [ ] Assets can be scraped from multiple sources for greater flexibility 
- [ ] Additional important portfolio metrics are available (e.g. Volatility, Sharpe Ratio, etc.)
- [ ] Portfolios can be deleted from main menu
- [ ] Machine learning techniques implemented to evaluate individual asset performance
