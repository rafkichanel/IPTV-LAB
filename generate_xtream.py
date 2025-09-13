import json
import requests
import re
import time

# ===============================
# 1. BACA DAFTAR USER
# ===============================
try:
    with open("users.json", "r", encoding="utf-8") as f:
        USERS = json.load(f)
except FileNotFoundError:
    print("❌ users.json tidak ditemukan")
    USERS = []

# ===============================
# 2. BACA DAFTAR SUMBER DARI sources.txt
# ===============================
try:
    with open("sources.txt", "r", encoding="utf-8") as f:
        sources = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("❌ sources.txt tidak ditemukan")
    sources = []

if not sources:
    print("⚠️ Tidak ada sumber di sources.txt, skrip berhenti.")
    exit()

# ===============================
# 3. GABUNGKAN PLAYLIST
# ===============================
playlist_content = "#EXTM3U\n"

for url in sources:
    for attempt in range(3):  # retry 3x jika gagal
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                text = r.text

                # HAPUS LOGO DEFAULT, GANTI DENGAN NAMA CHANNEL (per baris)
                new_lines = []
                for line in text.splitlines():
                    if 'LOGO="' in line:
                        tvg_name_match = re.search(r'tvg-name="(.*?)"', line)
                        logo_new = tvg_name_match.group(1) if tvg_name_match else ""
                        line = re.sub(r'LOGO=".*?"', f'LOGO="{logo_new}"', line)
                    new_lines.append(line)
                playlist_content += "\n".join(new_lines) + "\n"

                print(f"[OK] {url}")
                break
            else:
                print(f"[FAIL] {url} -> {r.status_code}")
        except Exception as e:
            print(f"[ERROR] {url} -> {e}")
            time.sleep(3)

# ===============================
# 4. SIMPAN PLAYLIST FINAL
# ===============================
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(playlist_content)

# ===============================
# 5. GENERATE XTREAM JSON
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

print("✓ playlist.m3u dan xtream.json berhasil dibuat")
