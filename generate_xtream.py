import os, json

# Baca sources
with open("sources.txt") as f:
    sources = [line.strip() for line in f if line.strip()]

# Baca users
with open("users.json") as f:
    users = json.load(f)

# Buat folder output
os.makedirs("output", exist_ok=True)

for user in users:
    uname, passwd = user["username"], user["password"]

    # Playlist M3U
    with open(f"output/get_{uname}_{passwd}.m3u", "w") as f:
        f.write("#EXTM3U\n")
        for i, src in enumerate(sources, start=1):
            f.write(f"#EXTINF:-1 group-title=\"AUTO\", Channel {i}\n{src}\n")

    # API JSON (Xtream style)
    api = {
        "user_info": {
            "username": uname,
            "password": passwd,
            "auth": 1
        },
        "available_channels": [
            {"num": i+1, "name": f"Channel {i+1}", "stream_url": src}
            for i, src in enumerate(sources)
        ]
    }
    with open(f"output/player_api_{uname}_{passwd}.json", "w") as f:
        json.dump(api, f, indent=2)

print("✅ Xtream files generated in /output")
