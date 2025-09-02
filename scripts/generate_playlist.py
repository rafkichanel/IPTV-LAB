import requests
import os
from datetime import datetime

# Lokasi sources.txt (ada di folder scripts)
BASE_DIR = os.path.dirname(__file__)
SOURCE_FILE = os.path.join(BASE_DIR, "sources.txt")

# Output disimpan di folder scripts juga
OUTPUT_FILE = os.path.join(BASE_DIR, "Finalplay.m3u")
LAST_UPDATE_FILE = os.path.join(BASE_DIR, "last_update.txt")

def fetch_sources():
    """Baca daftar URL dari sources.txt"""
    if not os.path.exists(SOURCE_FILE):
        print("❌ sources.txt tidak ditemukan")
        return []

    with open(SOURCE_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]
    return urls

def generate_playlist(urls):
    """Tulis daftar URL ke file M3U"""
    with open(OUTPUT_FILE, "w") as f:
        f.write("#EXTM3U\n")
        for i, url in enumerate(urls, 1):
            f.write(f"#EXTINF:-1,Channel {i}\n{url}\n")
    print(f"✅ Playlist berhasil dibuat: {OUTPUT_FILE}")

def update_last_time():
    """Catat waktu update terakhir"""
    with open(LAST_UPDATE_FILE, "w") as f:
        f.write(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    print("🕒 last_update.txt diperbarui")

if __name__ == "__main__":
    urls = fetch_sources()
    if urls:
        generate_playlist(urls)
        update_last_time()
    else:
        print("⚠️ Tidak ada URL di sources.txt")
