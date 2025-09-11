import json
import requests

# === BACA DAFTAR USER ===
try:
    with open("users.json", "r") as f:
        USERS = json.load(f)
except FileNotFoundError:
    print("❌ users.json tidak ditemukan")
    USERS = []

# === BACA DAFTAR SUMBER ===
try:
    with open("sources.txt", "r") as f:
        sources = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("❌ sources.txt tidak ditemukan")
    sources = []

# === GABUNGKAN SEMUA PLAYLIST ===
playlist_content = "#EXTM3U\n"

for url in sources:
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            playlist_content += r.text + "\n"
            print(f"[OK] {url}")
        else:
            print(f"[FAIL] {url} -> {r.status_code}")
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")

# === SIMPAN PLAYLIST FINAL ===
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(playlist_content)

# === GENERATE DATA XTREAM ===
xtream_data = {
    "user_info": [
        {
            "username": u.get("username"),
            "password": u.get("password"),
            "status": "Active"
        }
        for u in USERS
    ],
    "playlist_url": "playlist.m3u"
}

with open("xtream.json", "w", encoding="utf-8") as f:
    json.dump(xtream_data, f, indent=2)

print("✅ playlist.m3u dan xtream.json berhasil dibuat")
