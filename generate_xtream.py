import json
import requests
import re
import time

# ===============================
# 1. BACA DAFTAR USER
# ===============================
try:
    with open("users.json", "r") as f:
        USERS = json.load(f)
except FileNotFoundError:
    print("❌ users.json tidak ditemukan")
    USERS = []

# ===============================
# 2. AMBIL DAFTAR NEGARA & KATEGORI DARI IPTV-ORG
# ===============================
BASE_URL = "https://iptv-org.github.io/iptv/"

# Ambil daftar negara
countries_url = BASE_URL + "countries.json"
categories_url = BASE_URL + "categories.json"

def fetch_json(url):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.json()
        else:
            print(f"[FAIL] {url} -> {r.status_code}")
            return {}
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
        return {}

countries = fetch_json(countries_url)  # dict of {"id": "Indonesia", ...}
categories = fetch_json(categories_url)  # dict of {"news": "News", ...}

# ===============================
# 3. GENERATE SEMUA LINK M3U
# ===============================
sources = []

# Tambahkan semua negara
for code in countries.keys():
    sources.append(f"{BASE_URL}countries/{code}.m3u")

# Tambahkan semua kategori
for cat in categories.keys():
    sources.append(f"{BASE_URL}categories/{cat}.m3u")

print(f"🔹 Total sources: {len(sources)}")

# ===============================
# 4. GABUNGKAN PLAYLIST
# ===============================
playlist_content = "#EXTM3U\n"

for url in sources:
    for attempt in range(3):  # retry 3x jika gagal
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                text = r.text

                # HAPUS LOGO DEFAULT, GANTI DENGAN NAMA CHANNEL
                # Jika ada tvg-name, gunakan untuk logo
                text = re.sub(
                    r'LOGO=".*?"',
                    lambda m: f'LOGO="{re.search(r"tvg-name=\"(.*?)\"", m.string).group(1) if re.search(r"tvg-name=\"(.*?)\"", m.string) else ""}"',
                    text
                )

                playlist_content += text + "\n"
                print(f"[OK] {url}")
                break
            else:
                print(f"[FAIL] {url} -> {r.status_code}")
        except Exception as e:
            print(f"[ERROR] {url} -> {e}")
            time.sleep(3)

# ===============================
# 5. SIMPAN PLAYLIST FINAL
# ===============================
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(playlist_content)

# ===============================
# 6. GENERATE XTREAM JSON
# ===============================
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
