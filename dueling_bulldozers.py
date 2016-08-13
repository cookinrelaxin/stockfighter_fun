import requests
import json
import time

import multiprocessing
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def reset():
    r.set('qty_bought', 0)
    r.set('qty_outstanding', 0)

    r.set('num_asks', 0)
    r.set('avg_ask_price', 0)

    r.set('num_bids', 0)
    r.set('avg_bid_price', 0)

def int_from_str(i):
    return int(float(i))

def get_qty_bought():
    return int_from_str(r.get('qty_bought'))

def inc_qty_bought(inc):
    return int_from_str(r.incr('qty_bought', inc))

def get_qty_outstanding():
    return int_from_str(r.get('qty_outstanding'))

def inc_qty_outstanding(inc):
    return int_from_str(r.incr('qty_outstanding', inc))

def dec_qty_outstanding(dec):
    return int_from_str(r.decr('qty_outstanding', dec))


# def get_avg_price():
#     return int_from_str(r.get('avg_price'))
# 
# def update_avg_price(price, quantity):
#     curr = get_avg_price()
#     update = (curr + (price * quantity)) / float(quantity + 1)
#     r.set('avg_price', update)

def get_num_asks():
    return int_from_str(r.get('num_asks'))

def inc_num_asks():
    return int_from_str(r.incr('num_asks'))

def get_avg_ask_price():
    return int_from_str(r.get('avg_ask_price'))

def update_avg_ask_price(price):
    curr_avg = get_avg_ask_price()
    total_num_asks = get_num_asks()
    update = (total_num_asks * curr_avg + price) / float(total_num_asks + 1)
    r.set('avg_ask_price', update)

def get_num_bids():
    return int_from_str(r.get('num_bids'))

def inc_num_bids():
    return int_from_str(r.incr('num_bids'))

def get_avg_bid_price():
    return int_from_str(r.get('avg_bid_price'))

def update_avg_bid_price(price):
    curr_avg = get_avg_bid_price()
    total_num_bids = get_num_bids()
    update = (total_num_bids * curr_avg + price) / float(total_num_bids + 1)
    r.set('avg_bid_price', update)

reset()

API_key = "5980fe4a7a7650595436ef1b2ec193836252cac8"

root_url = "https://api.stockfighter.io/ob/api/"
headers = {"X-Starfighter-Authorization": API_key}

account = "SSM34294811"

SYMBOL = "VIQ" 
VENUE = "EKAEX" 

def check_API_up():
    heartbeat = requests.get(root_url+"heartbeat", headers=headers) 
    assert heartbeat.status_code == 200 
    heartbeat_json = json.loads(heartbeat.text) 
    assert heartbeat_json["ok"] == True 
    assert heartbeat_json["error"] == "" 

check_API_up()

#venue is a ticker symbol not the full name
def check_venue_up(venue):
    heartbeat = requests.get(root_url+"/venues/"+venue+"/heartbeat", headers=headers) 
    assert heartbeat.status_code == 200 
    heartbeat_json = json.loads(heartbeat.text) 
    assert heartbeat_json["ok"] == True 
    assert heartbeat_json["venue"] == venue 

check_venue_up("TESTEX")
check_venue_up(VENUE)

def stocks_for_venue(venue):
    res = requests.get(root_url+"/venues/"+venue+"/stocks", headers=headers) 
    assert res.status_code == 200 
    res_json = json.loads(res.text) 
    assert res_json["ok"] == True 
    stocks = res_json["symbols"] 
    return stocks 

#print stocks_for_venue("KRNEX") 

def orderbook_for_stock(venue, symbol):
    res = requests.get(root_url+"/venues/"+venue+"/stocks/"+symbol, headers=headers) 
    assert res.status_code == 200 
    res_json = json.loads(res.text) 
    assert res_json["ok"] == True 
    assert res_json["venue"] == venue 
    assert res_json["symbol"] == symbol 

    bids = res_json["bids"] 
    return bids 

#print orderbook_for_stock("KRNEX", "UUSJ")

def place_order(account="EXB123456", venue="TESTEX", stock="FOOBAR", price=5342, qty=3, direction="buy", orderType="limit"): 
    payload = {
            'account': account,
            'venue': venue,
            'stock': stock,
            'price': price,
            'qty': qty,
            'direction': direction,
            'orderType': orderType
    }
    url = root_url+"/venues/"+venue+"/stocks/"+stock+"/orders"
    res = requests.post(url, headers=headers, data=json.dumps(payload)) 
    assert res.status_code == 200 

    res_json = json.loads(res.text) 
    assert res_json["ok"] == True 
    assert res_json["symbol"] == stock 
    assert res_json["venue"] == venue 
    assert res_json["direction"] == direction 
    assert res_json["orderType"] == orderType
    assert res_json["account"] == account 
    return res_json

def order_status(order_id="10287", venue="TESTEX", stock="FOOBAR"):
    payload = {
            'id': order_id,
            'venue': venue,
            'stock': stock
    }
    url = root_url+"/venues/"+venue+"/stocks/"+stock+"/orders/"+order_id
    res = requests.get(url, headers=headers, data=json.dumps(payload)) 
    assert res.status_code == 200 

    res_json = json.loads(res.text) 
    assert res_json["ok"] == True 
    assert res_json["symbol"] == stock 
    assert res_json["venue"] == venue 
    return res_json

def get_quote(venue='TESTEX', stock='FOOBAR'):
    payload = {
            'venue': venue,
            'stock': stock
    }
    url = root_url+"/venues/"+venue+"/stocks/"+stock+"/quote"
    res = requests.get(url, headers=headers, data=json.dumps(payload)) 
    assert res.status_code == 200 

    res_json = json.loads(res.text) 

    assert res_json["ok"] == True 
    assert res_json["symbol"] == stock 
    assert res_json["venue"] == venue 

    return res_json

def cancel_order(venue="TESTEX", stock=SYMBOL, order_id="234"):
    payload = {
            'order': order_id,
            'venue': venue,
            'stock': stock
    }
    url = root_url+"/venues/"+venue+"/stocks/"+stock+"/orders/"+order_id
    res = requests.delete(url, headers=headers, data=json.dumps(payload)) 
    assert res.status_code == 200 

    res_json = json.loads(res.text) 
    assert res_json["ok"] == True 
    assert res_json["symbol"] == stock 
    assert res_json["venue"] == venue 
    return res_json

def order_book(venue="TESTEX", stock=SYMBOL):
    payload = {
            'venue': venue,
            'stock': stock
    }
    url = root_url+"/venues/"+venue+"/stocks/"+stock
    res = requests.get(url, headers=headers, data=json.dumps(payload)) 
    assert res.status_code == 200 

    res_json = json.loads(res.text) 
    assert res_json["ok"] == True 
    assert res_json["symbol"] == stock 
    assert res_json["venue"] == venue 
    return res_json

#keep two averages: average lowest bid, average highest ask
#the strategy implemeted here is to constantly update those averages and execute bids lower than the average lowest bid, and asks higher than the average highest ask
#seems to work
def market_make():
    MAX_OUTSTANDING = 500 
    MIN_OUTSTANDING = -500 
    DEFAULT_QTY = 100
    DEFAULT_DELAY = 0.1
    DEFAULT_PRICE = 2100
    BID_SIZE_FRAC = 1.0
    TIME_TO_WAIT = 1.0
    AVG_OFFSET = 100
    
    NUM_PROCESSES = 5
    
    def buy_loop():
        print "start buy loop"
        while True:


            if (get_qty_outstanding() < MAX_OUTSTANDING):

                quote = get_quote(venue=VENUE, stock=SYMBOL)

                qty = DEFAULT_QTY
                bid = 0
                try:
                    bid = quote["bid"]
                except:
                    continue
                update_avg_bid_price(bid)
                inc_num_bids()
                price = get_avg_bid_price() - AVG_OFFSET
                #price = bid - AVG_OFFSET
        
                order = place_order(account=account, venue=VENUE, stock=SYMBOL, price=price, qty=qty, direction="buy", orderType="limit")
                order_id = order["id"]
                order_placed_time = time.time()
                total_filled = 0

                while (total_filled < qty) and (time.time() < (order_placed_time + TIME_TO_WAIT)):
                    status = order_status(order_id=str(order_id), venue=VENUE, stock=SYMBOL)
                    total_filled = status["totalFilled"]
                    time.sleep(DEFAULT_DELAY)

                else:
                    cancel_status = cancel_order(venue=VENUE, stock=SYMBOL, order_id=str(order_id))
                    total_filled = cancel_status["totalFilled"]
        
                inc_qty_outstanding(total_filled)


            else:
                time.sleep(DEFAULT_DELAY)

    def sell_loop():
        print "start sell loop"
        #while get_profit() <= TARGET_PROFIT:
        while True:
            if (get_qty_outstanding() > MIN_OUTSTANDING):

                quote = get_quote(venue=VENUE, stock=SYMBOL)

                qty = DEFAULT_QTY
                ask = 0
                try:
                    ask = quote["ask"]
                except:
                    continue
                update_avg_ask_price(ask)
                inc_num_asks()
                price = get_avg_ask_price() + AVG_OFFSET
        
                order = place_order(account=account, venue=VENUE, stock=SYMBOL, price=price, qty=qty, direction="sell", orderType="limit")
                order_id = order["id"]
                order_placed_time = time.time()
                total_filled = 0

                while (total_filled < qty) and (time.time() < (order_placed_time + TIME_TO_WAIT)):
                    status = order_status(order_id=str(order_id), venue=VENUE, stock=SYMBOL)
                    total_filled = status["totalFilled"]
                    time.sleep(DEFAULT_DELAY)

                else:
                    cancel_status = cancel_order(venue=VENUE, stock=SYMBOL, order_id=str(order_id))
                    total_filled = cancel_status["totalFilled"]
        
                dec_qty_outstanding(total_filled)

            else:
                time.sleep(DEFAULT_DELAY)

    for n in range(NUM_PROCESSES):
        buy = multiprocessing.Process(target=buy_loop)
        buy.start()

        sell = multiprocessing.Process(target=sell_loop)
        sell.start()

market_make()
