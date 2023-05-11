import requests
import sqlite3
import asyncio
import json
import locale
import sqlite3
import sys
import time

from flask import Flask, jsonify, render_template, request
from requests import get
from random import choice, choices, randint

locale.setlocale(locale.LC_ALL, "")


def intcomma(value):
    return locale.format_string("%d", int(value), grouping=True)


def get_asset_id(asset_name):
    # Connect to the SQLite database
    conn = sqlite3.connect("./databases/roblox_assets.db")
    c = conn.cursor()

    # Search the database for the asset ID
    c.execute("SELECT asset_id FROM assets WHERE name = ?", (asset_name,))
    result = c.fetchone()

    # Close the database connection
    conn.close()

    if result is not None:
        asset_id = result[0]
        return asset_id
    else:
        return None


def get_thumbnail(asset_id):
    url = "https://thumbnails.roblox.com/v1/batch"
    data = [
        {
            "requestId": f"{asset_id}:undefined:Asset:150x150:null:regular",
            "type": "Asset",
            "targetId": asset_id,
            "format": "png",
            "size": "150x150",
        }
    ]

    response = requests.post(url, json=data)
    data = response.json()["data"]
    return data[0]["imageUrl"]



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
        variable = [
            "item_name",
            "acro",
            "rap",
            "value",
            "default_value",
            "demand",
            "trend",
            "projected",
            "hyped",
            "rare",
        ][self.index]
        result = [f"{variable}", f"{getattr(self, variable)}\n"]
        self.index += 1
        return result



def get_cached_api_result(url):
    """
    Returns cached API result if available and not expired, otherwise fetches new result and caches it.
    Caches API result for 10 minutes.
    """
    cache = get_cached_api_result.cache
    if url in cache and time.time() - cache[url]["timestamp"] < 604800:
        print("CACHED")
        return cache[url]["result"]
    else:
        response = get(url).json()
        cache[url] = {"result": response, "timestamp": time.time()}
        return response


get_cached_api_result.cache = {}


def create_db():
    conn = sqlite3.connect("./databases/items.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS items
                (item_name TEXT, rap INT, count INT, img_url TEXT)"""
    )

    conn.commit()
    conn.close()


def add_item_to_db(item_name, rap, img_url, count=1):
    conn = sqlite3.connect("./databases/items.db")
    c = conn.cursor()

    # Check if the item already exists in the database
    c.execute("SELECT * FROM items WHERE item_name = ?", (item_name,))
    result = c.fetchone()

    if result is None:
        # Item does not exist, add a new row
        c.execute(
            "INSERT INTO items (item_name, rap, img_url, count) VALUES (?, ?, ?, ?)",
            (item_name, rap, img_url, count),
        )
    else:
        # Item already exists, update count
        c.execute(
            "UPDATE items SET count = count + ? WHERE item_name = ?", (count, item_name)
        )

    conn.commit()
    conn.close()


def get_items_from_db():
    conn = sqlite3.connect("./databases/items.db")
    c = conn.cursor()
    c.execute(
        "SELECT item_name, rap, count FROM items GROUP BY item_name ORDER BY rap DESC"
    )
    items = c.fetchall()
    conn.close()

    result = []
    for item in items:
        name, rap, count = item
        thumbnail = get_thumbnail(get_asset_id(name))
        result.append(
            {"name": name, "rap": rap, "count": count, "thumbnail": thumbnail}
        )

    return result


def get_money_from_db():
    conn = sqlite3.connect("./databases/money.db")

    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS cur
                (money INT)"""
    )

    c.execute("SELECT * FROM cur")

    items = c.fetchone()
    conn.close()

    if not items:
        items = 0

    return items


def update_money_in_db(profit):
    conn = sqlite3.connect("./databases/money.db")

    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS cur
                (money INT)"""
    )

    c.execute("SELECT * FROM cur")

    # If the table is empty, initialize it with 0 money
    if not (curm := c.fetchall()):
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
        item = Item(items_list[item_choice[i - 1]])
        x.append(item)

    return x


def get_trade_offers(itm, name=""):
    amnt = randint(1, 4)
    value_range = (int(itm[1]) * 0.7, int(itm[1]) * 1.3)

    response = get_cached_api_result("https://www.rolimons.com/itemapi/itemdetails")
    items_list = response["items"].items()

    total_value = 0
    trade_offers = []

    while len(trade_offers) < amnt and total_value < value_range[1]:
        trade_itm = choice(list(items_list))
        item_value = trade_itm[1][4]

        if total_value + item_value > value_range[1] or trade_itm[1][0] == name:
            pass
        else:
            if value_range[0] <= total_value + item_value <= value_range[1]:
                trade_offers.append(
                    (trade_itm[1][0], int(item_value), get_thumbnail(trade_itm[0]))
                )
                total_value += item_value

    return trade_offers
