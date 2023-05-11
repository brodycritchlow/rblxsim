from utility import *

app = Flask(
    __name__,
    static_folder=r"C:\Users\brody\OneDrive\Documents\Chip8_Emulator\templates\static",
)


@app.route("/")
def index():
    create_db()
    items = get_items_from_db()
    current_currency = get_money_from_db()
    return render_template(
        "index.html", items=items, current_currency=get_money_from_db()
    )


@app.route("/coinflip")
@app.route("/conflip/")
def coinflip():
    return render_template("coinflip.html", current_currency=get_money_from_db())


@app.route("/bet/<bet>", methods=["POST"])
def bet(bet):
    x = choice(["Heads", "Tails"])

    bet = int(bet)

    if bet < get_money_from_db()[0]:
        if x == "Heads":
            update_money_in_db(bet)
        else:
            update_money_in_db(-bet)

        return jsonify({"success": True, "flip": x})
    return jsonify({"success": False, "flip": None})


@app.route("/market")
@app.route("/market/")
def market():
    items = get_rand(9)
    items = sorted(items, key=lambda x: x.default_value, reverse=True)
    current_currency = get_money_from_db()
    return render_template(
        "market.html", market_items=items, current_currency=get_money_from_db()
    )


@app.route("/sell/<item_name>", methods=["POST", "GET"])
def sell_item(item_name):
    conn = sqlite3.connect("./databases/items.db")
    c = conn.cursor()
    c.execute("SELECT rap, count FROM items WHERE item_name = ?", (item_name,))

    result = c.fetchone()
    if result is None:
        conn.close()
        return jsonify({"success": False, "message": "Item not found"})

    total_rap, count = result
    if count == 1:
        c.execute("DELETE FROM items WHERE item_name = ?", (item_name,))
    else:
        c.execute(
            "UPDATE items SET count = count - 1 WHERE item_name = ?", (item_name,)
        )

    conn.commit()
    conn.close()

    profit = total_rap * 0.7

    update_money_in_db(profit)

    return jsonify({"success": True, "rap": total_rap})


@app.route("/buy/", methods=["POST", "GET"])
def buy_item():
    itm_name = json.loads(request.data).get("item_name")
    itm_rap = json.loads(request.data).get("item_rap")

    conn = sqlite3.connect("./databases/items.db")
    c = conn.cursor()

    cur_money = get_money_from_db()[0]

    if int(cur_money) < int(itm_rap):
        jsonify({"success": False})
    else:
        add_item_to_db(
            item_name=itm_name,
            rap=itm_rap,
            img_url=get_thumbnail(get_asset_id(itm_name)),
        )
        update_money_in_db(-int(itm_rap))

        return jsonify({"success": True})


@app.route("/trade_offers/<item_name>")
def trade_offers(item_name):
    conn = sqlite3.connect("./databases/items.db")
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE item_name = ?", (item_name,))
    item_data = c.fetchone()

    # print(item_data)
    conn.close()

    if not item_data:
        return jsonify({"success": False})

    trade_offers = get_trade_offers(item_data, item_name)

    total_rap = sum(item[1] for item in trade_offers)

    return render_template(
        "trade_offers.html",
        item_data=[item_data],
        trades=sorted(trade_offers, key=lambda x: x[1], reverse=True),
        total_rap=total_rap,
    )


@app.route("/click")
@app.route("/click/")
def click():
    return jsonify({"success": True, "new": update_money_in_db(500)})


@app.route("/accept/", methods=["POST"])
def accept():
    your_item = json.loads(request.data).get("itemName")
    offer_items = json.loads(request.data).get("itemNames")
    default_values = json.loads(request.data).get("defaultValues")

    # Update count of your_item in items.db
    conn = sqlite3.connect("./databases/items.db")
    c = conn.cursor()

    c.execute(
        "SELECT rap, count FROM items WHERE item_name = ? GROUP BY item_name",
        (your_item,),
    )
    results = c.fetchall()
    if len(results) == 0:
        conn.close()
        return jsonify({"success": False, "message": "Item not found"})

    total_rap = sum([result[0] for result in results])
    total_count = sum([result[1] for result in results])

    if total_count > 1:
        c.execute(
            "UPDATE items SET count = count - 1 WHERE item_name = ?", (your_item,)
        )
        conn.commit()
    else:
        c.execute("DELETE FROM items WHERE item_name = ?", (your_item,))
        conn.commit()

    # Add all the offered items to the database
    for i, item in enumerate(offer_items):
        c.execute(
            "INSERT INTO items (item_name, rap, img_url, count) VALUES (?, ?, ?, ?)",
            (
                item.strip(),
                default_values[i].replace(",", ""),
                get_thumbnail(get_asset_id(item.strip())),
                1,
            ),
        )
        conn.commit()

    conn.close()

    return jsonify({"success": True})

def printf(st):
    print("DEBUG:", st)

if __name__ == "__main__":
    app.jinja_env.filters["intcomma"] = intcomma
    app.jinja_env.filters["print"] = printf
    app.run(debug=False)
