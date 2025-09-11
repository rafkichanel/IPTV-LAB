import json
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# Baca daftar user dari users.json
with open("users.json", "r") as f:
    USERS = {u["username"]: u["password"] for u in json.load(f)}

# Baca playlist.m3u
with open("playlist.m3u", "r", encoding="utf-8") as f:
    PLAYLIST = f.read()

@app.route("/player_api.php")
def player_api():
    username = request.args.get("username")
    password = request.args.get("password")

    if username not in USERS or USERS[username] != password:
        return jsonify({"user_info": {"auth": 0, "status": "false"}})

    action = request.args.get("action")

    # Info login
    if not action:
        return jsonify({
            "user_info": {
                "auth": 1,
                "status": "Active",
                "username": username,
                "password": password
            },
            "server_info": {
                "url": request.host_url.strip("/"),
                "port": 80,
                "https_port": 443,
                "server_protocol": "http",
                "rtmp_port": "0",
                "timezone": "GMT+0"
            }
        })

    # Playlist dalam format M3U
    if action == "get_live_streams":
        return Response(PLAYLIST, mimetype="audio/x-mpegurl")

    return jsonify({"error": "unknown action"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
