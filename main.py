import time
from requests import get
from random import choices, randint, choice
import asyncio
from utility import get_asset_id, get_thumbnail
import sqlite3
import locale
import sys
import json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask, request, render_template, jsonify

app = Flask(__name__, static_folder=r"C:\Users\brody\OneDrive\Documents\Chip8_Emulator\templates\static")

limiter = Limiter(
    get_remote_address,
    app=app,
    retry_after="60"
)

if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

locale.setlocale(locale.LC_ALL, '')

class Item:
    def __init__(self, item_list):
        self.item_list = item_list
        self.item_name = item_list[0]
        self.acro = item_list[1]
        self.rap = item_list[2] if item_list[2] != 0 else 1_000_000_000
        self.value = item_list[3] if item_list[2] != 0 else 1_000_000_000
        self.default_value = int(item_list[4]) if item_list[2] != 0 else 1_000_000_000
        self.demand = item_list[5]
        self.trend = item_list[6]
        self.projected = item_list[7]
        self.hyped = item_list[8]
        self.rare = item_list[9]
        self.item_url = get_thumbnail(get_asset_id(item_list[0]))
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index >= len(self.item_list):
            raise StopIteration
        variables = ["item_name", "acro", "rap", "value", "default_value", "demand", "trend", "projected", "hyped", "rare"]
        result = [f"{variables[self.index]}", f"{getattr(self, variables[self.index])}\n"]
        self.index += 1
        return result


def get_cached_api_result(url):
    """
    Returns cached API result if available and not expired, otherwise fetches new result and caches it.
    Caches API result for 10 minutes.
    """
    cache = get_cached_api_result.cache
    if url in cache and time.time() - cache[url]["timestamp"] < 600:
        return cache[url]["result"]
    else:
        response = get(url).json()
        cache[url] = {"result": response, "timestamp": time.time()}
        return response


get_cached_api_result.cache = {}

def create_db():
    conn = sqlite3.connect('items.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items
                (item_name TEXT, rap INT, img_url TEXT)''')
    
    conn.commit()
    conn.close()

def add_item_to_db(rap, item_name, img_url):
    conn = sqlite3.connect('items.db')
    c = conn.cursor()
    c.execute("INSERT INTO items VALUES (?, ?, ?)", (item_name, rap, img_url))
    conn.commit()
    conn.close()

def get_items_from_db():
    conn = sqlite3.connect('items.db')
    c = conn.cursor()
    c.execute("SELECT * FROM items ORDER BY rap DESC")
    items = list(c.fetchall())

    for id, i in enumerate(items):
        i = list(i)
        if i[-1] != None:
            if "rbxcdn" in i[-1]:
                pass
            else:
                i[-1] = get_thumbnail(get_asset_id(i[0]))
                items[id] = i
        else:
            i[-1] = get_thumbnail(get_asset_id(i[0]))
            items[id] = i

    conn.close()
    return items

def get_money_from_db():
    conn = sqlite3.connect('money.db')
    
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cur
                (money INT)''')
    
    c.execute("SELECT * FROM cur")

    items = c.fetchone()
    conn.close()

    if not items:
        items = 0

    return items

def update_money_in_db(profit):
    conn = sqlite3.connect('money.db')
    
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cur
                (money INT)''')
    
    c.execute("SELECT * FROM cur")

    # If the table is empty, initialize it with 0 money
    if not (curm:=c.fetchall()):
        c.execute("INSERT INTO cur (money) VALUES (?)", (0,))
    
    c.execute("UPDATE cur SET money = money + ?", (profit,))
    
    conn.commit()
    conn.close()

    return curm[0][0] + profit



def get_rand(amnt):
    response = get_cached_api_result("https://www.rolimons.com/itemapi/itemdetails")
    items_list = response["items"]

    random_item_legend = list(items_list.keys())
    item_choice = choices(random_item_legend, k=amnt)

    x = []

    for i in range(amnt):
        item = Item(items_list[item_choice[i-1]])
        if item.rap != 1_000_000_000:
          x.append(item)
        

    return x


def intcomma(value):
    return locale.format_string("%d", value, grouping=True)

create_db()

def get_trade_offers(itm):
    amnt = randint(1, 4)
    value_range = (itm[1] * 0.9, itm[1] * 1.1)

    response = get_cached_api_result("https://www.rolimons.com/itemapi/itemdetails")
    items_list = response["items"].items()

    # Generate a list of item IDs within the desired value range
    items_within_range = [item[0] for item in items_list if value_range[0] <= item[1]["value"] <= value_range[1]]

    trade_offers = []
    total_value = 0

    # Randomly select items until the total value falls within the desired range
    while total_value < value_range[0] or total_value > value_range[1]:
        item_ids = choices(items_within_range, k=amnt)
        trade_offers = [Item(item_list=response["items"][item_id]) for item_id in item_ids]
        total_value = sum([item.default_value for item in trade_offers])

    return trade_offers

app.jinja_env.filters['intcomma'] = intcomma

@app.route('/')
def index():
    items = get_items_from_db()
    current_currency = get_money_from_db()
    return render_template('index.html', items=items, current_currency=get_money_from_db())

@app.route('/coinflip')
@app.route('/conflip/')
def coinflip():
    return render_template('coinflip.html', current_currency=get_money_from_db())

@app.route('/bet/<bet>', methods=["POST"])
def bet(bet):
    x = choice(["Heads", "Tails"])

    bet = int(bet)

    if x == "Heads":
        update_money_in_db(bet)
    else:
        update_money_in_db(-bet)

    return jsonify({'flip': x})

@app.route("/market")
@app.route('/market/')
def market():
    items = get_rand(9)
    items = sorted(items, key=lambda x: x.default_value, reverse=True)
    current_currency = get_money_from_db()
    return render_template('market.html', market_items=items, current_currency=get_money_from_db())

@app.route('/sell/<item_name>', methods=['POST', 'GET'])
def sell_item(item_name):
    conn = sqlite3.connect('items.db')
    c = conn.cursor()
    c.execute("SELECT rap, count(*) FROM items WHERE item_name = ? GROUP BY item_name", (item_name,))
    
    results = c.fetchall()
    if len(results) == 0:
        conn.close()
        return jsonify({'success': False, 'message': 'Item not found'})
    
    total_rap = sum([result[0] for result in results])
    total_count = sum([result[1] for result in results])
    
    c.execute("DELETE FROM items WHERE item_name = ?", (item_name,))
    
    conn.commit()
    
    if total_count > 1:
        c.execute("INSERT INTO items (item_name, rap) VALUES (?, ?)", (item_name, total_rap))
        conn.commit()
    
    conn.close()

    profit = total_rap * 0.7

    update_money_in_db(profit)

    return jsonify({'success': True, 'rap': total_rap})


@app.route('/buy/', methods=['POST', 'GET'])
def buy_item():
    itm_name = json.loads(request.data).get("item_name")
    itm_rap = json.loads(request.data).get("item_rap")

    conn = sqlite3.connect('items.db')
    c = conn.cursor()

    cur_money = get_money_from_db()[0]

    if int(cur_money) < int(itm_rap):
        jsonify({'success': False})
    else:
        add_item_to_db(item_name=itm_name, rap=itm_rap, img_url=get_thumbnail(get_asset_id(itm_name)))
        update_money_in_db(-int(itm_rap))

        return jsonify({'success': True})

@app.route('/trade_offers/<item_name>')
def trade_offers(item_name):
    conn = sqlite3.connect('items.db')
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE item_name = ?", (item_name,))
    item_data = c.fetchone()
    conn.close()

    if not item_data:
        return jsonify({"success": False})
        
    trade_offers = get_trade_offers(item_data)
    
    total_rap = sum(item.default_value for item in trade_offers)

    return render_template('trade_offers.html', item_data=item_data, trade_offers=sorted(trade_offers, key=lambda x: x.default_value, reverse=True), total_rap=total_rap)

    

# @app.route('/items/', methods=['POST'])
# def getMore():
#     for item in get_rand(3):
#         img_url = get_thumbnail(get_asset_id(item.item_name))
#         add_item_to_db(item.default_value, item.item_name, img_url)

#     return jsonify({"success": True})

@app.route('/click')
@app.route('/click/')
@limiter.limit("7/second")
def click():
    return jsonify({"success": True, "new": update_money_in_db(500)})

@app.route('/accept/', methods=['POST'])
def accept():
    your_item = json.loads(request.data).get('itemName')
    offer_items = json.loads(request.data).get('itemNames')
    default_values = json.loads(request.data).get('defaultValues')

    # Remove your_item from items.db
    conn = sqlite3.connect('items.db')
    c = conn.cursor()
    data = json.loads(request.data)

    # Remove the item being traded from the database
    c.execute("DELETE FROM items WHERE item_name=?", (your_item,))
    conn.commit()

    # Add all the offered items to the database
    for i, item in enumerate(offer_items):
        c.execute("INSERT INTO items (item_name, rap, img_url) VALUES (?, ?, ?)", (item.strip(), default_values[i], get_thumbnail(get_asset_id(item.strip()))))
        conn.commit()

    return jsonify({"success": True})


if __name__ == '__main__':
    app.run(debug=True)
