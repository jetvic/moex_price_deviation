import requests
import datetime
from variables import tg_token, tg_chat_id

deviation = 40
sid = 'SBER'
file_sids = open("tickers.txt", "r")
start_date = datetime.date.today() - datetime.timedelta(weeks=11)

tickers40 = []
watchlist = ['SBER', 'SBERP', 'PLZL', 'YNDX', 'AFKS']
current_prices = ['=========\n']


def indicator(sid):
    url1 = 'https://iss.moex.com/iss/engines/stock/markets/shares/securities/{}/security.json?'.format(sid)
    params1 = {'iss.meta': 'off', 'iss.only': 'marketdata', 'marketdata.columns': 'BOARDID,LAST'}
    req = requests.get(url=url1, params=params1)
    json1 = req.json()

    url2 = 'http://iss.moex.com/iss/history/engines/stock/markets/shares/sessions/main/boards/TQBR/securities/{}/security.json?'.format(
        sid)
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

    # Find close price for every fridays:
    fridays_price = []
    for friday in fridays:
        fridays_price.append(day_prices[friday])

    # Calculate value of Indicator "40%":
    # current price:
    last = (dict(json1['marketdata']['data'])['TQBR'])
    if sid in watchlist:
        current_prices.append(f"{sid} {last}\n")
    # current close price:
    # last = list(day_prices.values())[-1]
    # last 9 week close prices:
    last9 = fridays_price[-10:-1]
    average10 = (sum(last9) + last) / (len(last9) + 1)
    idicator40 = round((last / average10 - 1) * 100, 1)
    if idicator40 > deviation:
        print(sid, idicator40, f"{deviation} !!!")
        tickers40.append(f"{sid} {idicator40}\n")
    elif idicator40 < -deviation:
        print(sid, idicator40, f"-{deviation} !!!")
        tickers40.append(f"{sid} {idicator40}\n")
    else:
        print(sid, idicator40)


def send_message(text):
    token = tg_token
    chat_id = tg_chat_id
    url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text
    results = requests.get(url_req)
    print(results.json())


while True:
    line = file_sids.readline().strip()
    if not line:
        break
    try:
        indicator(line)
    except (IndexError, TypeError, KeyError):
        pass
file_sids.close()

res_list = tickers40 + current_prices
text = "".join(res_list)
send_message(text)
