from flask import Flask, render_template, send_from_directory
from html import escape
import requests
import PythonWalker as pw
import threading
import time
from websockets.exceptions import ConnectionClosedError as ConnectionClosedError

EMAIL = "example@example.com" #CHANGE
PASSWORD = "password123" #CHANGE

VERSION = "1.0.0"

print("Getting room type...")
room_type = requests.get("https://game.pixelwalker.net/listroomtypes").json()[0]
print(f"Room Type is: {room_type}")

print("Logging in...")
USER = pw.login_with_pass(EMAIL, PASSWORD)
print(f"Logged in as: {USER.username}")

app = Flask(__name__)

@app.route('/')
def index():
    r = requests.get(f"https://game.pixelwalker.net/room/list/{room_type}")
    data = r.json()
    ponline = data["onlinePlayerCount"]
    wonline = data["onlineRoomCount"]
    worlds = sorted(data["visibleRooms"], key=lambda x: (x["players"], x["data"]["plays"]), reverse=True)
    new_worlds = []
    for world in worlds:
        if world["data"]["worldType"] == 0:
            world["icon"] = "fa-circle"
        elif world["data"]["worldType"] == 1:
            world["icon"] = "fa-hourglass-half"
        elif world["data"]["worldType"] == 2:
            world["icon"] = "fa-box-archive"
        world["data"]["title"] = escape(world["data"]["title"], quote=True)
        world["data"]["description"] = escape(world["data"]["description"], quote=True)
        new_worlds.append(world)
    worlds = new_worlds
    return render_template("index.html", worlds=worlds, ponline=ponline, wonline=wonline, version=VERSION)
    
@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory('assets', filename)
    
@app.route('/world-info/<id>')
def get_world_info(id):
    players = {}
    def on_init(conn, packet):
        threading.Thread(target=shutdown, args=(conn,)).start()
        
    def shutdown(conn):
        time.sleep(1)
        conn.websocket.close()
        
    def on_join(conn, packet):
        nonlocal players
        players = conn.players
        
    try:
        pw.connect(id, USER, on_init=on_init, on_join=on_join, custom_init=False)
    except ConnectionClosedError:
        pass
        
    usernames = []
    for key, value in players.items():
        print(key)
        print(value)
        usernames.append(value)
        
    players = usernames
    
    return render_template("worldinfo.html", players=players)
    
@app.route('/favicon.ico')
def icon():
    return send_from_directory('', "icon.png")

if __name__ == '__main__':
    app.run(debug=True)