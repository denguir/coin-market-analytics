#!/bin/sh
cd /home/coin-market-analytics
python3 main.py $SLACK_CRYPTO_EVENTS
git pull origin master
git add .
git commit -a -m "database update"
git push origin master
