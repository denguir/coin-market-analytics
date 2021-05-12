# Coin market analytics
This is a small set of script that extracts incoming crypto-related events from [Coinmarketcal](https://coinmarketcal.com/en/). A server is configured to extract every day at 18h UTC the incoming events of the next month:

* Each positive event is posted on Slack (#crypto-events) with the 24h price change in BTC
* An event database is completed to allow future backtesting strategies