#!/bin/sh

python3 /home/coin-market-analytics/main.py
git -C /home/coin-market-analytics pull origin master
git -C /home/coin-market-analytics add .
git -C /home/coin-market-analytics commit -a -m "database update"
git -C /home/coin-market-analytics push origin master
