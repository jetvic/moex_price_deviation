#! /usr/bin/env python3
import requests
import datetime

sid = 'SBER'
file_sids = open("tickers.txt", "r")
start_date = datetime.date.today()-datetime.timedelta(weeks=11)

def Indicator(sid):
    url1 = 'https://iss.moex.com/iss/engines/stock/markets/shares/securities/{}/security.json?'.format(sid)
    params1 = {'iss.meta': 'off', 'iss.only': 'marketdata', 'marketdata.columns': 'BOARDID,LAST'}
    req = requests.get(url=url1, params=params1)
    json1 = req.json()

    url2 = 'http://iss.moex.com/iss/history/engines/stock/markets/shares/sessions/main/boards/TQBR/securities/{}/security.json?'.format(sid)
    params2 = {'history.columns': 'TRADEDATE,LEGALCLOSEPRICE', 'from': '{}'.format(start_date), 'iss.meta': 'off'}
    res = requests.get(url=url2, params=params2)
    json2 = res.json()
    day_prices = dict(json2['history']['data'])
    days = list(day_prices.keys())
    # Find fridays in trade days:
    fridays = []
    for day in days:
        day_f = datetime.datetime.strptime(day, '%Y-%m-%d')
        if datetime.datetime.weekday(day_f) == 4:
            fridays.append(day)

    # Find close price for fridays:
    fridays_price = []
    for friday in fridays:
        fridays_price.append(day_prices[friday])

    # Calculate value of Indicator:
    # current price:
    last = (dict(json1['marketdata']['data'])['TQBR'])
    # last 9 week close prices:
    last9 = fridays_price[-10:-1]
    average10 = (sum(last9) + last) / (len(last9) + 1)
    idicator = round((last / average10 - 1) * 100, 1)
    if idicator > 20:
        print(sid, idicator, '< ----------------------- >20!')
    elif idicator < -20:
        print(sid, idicator, '< ----------------------- <-20!')
    else:
        print(sid, idicator)

while True:
    line = file_sids.readline().strip()
    if not line:
        break
    try:
        Indicator(line)
    except (IndexError,TypeError,KeyError):
        pass
file_sids.close()
