#!/bin/sh
cd /home/coin-market-analytics
python3 main.py
git pull origin master
git add .
git -a -m "database update"
git push origin master
