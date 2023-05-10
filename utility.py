import requests
import sqlite3

def get_asset_id(asset_name):
    # Connect to the SQLite database
    conn = sqlite3.connect('roblox_assets.db')
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
    url = 'https://thumbnails.roblox.com/v1/batch'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'x-csrf-token': 'ZigAhRc4zyYr'
    }
    data = [
        {
            "requestId": f"{asset_id}:undefined:Asset:150x150:null:regular",
            "type": "Asset",
            "targetId": asset_id,
            "format": "png",
            "size": "150x150"
        }
    ]

    response = requests.post(url, headers=headers, json=data)
    return response.json()["data"][0]["imageUrl"]

