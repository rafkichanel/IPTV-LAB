import requests
import os
from datetime import datetime

# Lokasi file sumber dan hasil
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder scripts
SOURCE_FILE = os.path.join(BASE_DIR, "sources.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "Finalplay.m3u")
LAST_UPDATE_FILE = os.path.join(BASE_DIR, "last_update.txt")

def fetch_and_combine_sources():
    """Mengambil konten M3U dari semua URL di sources.txt dan menggabungkannya."""
    # Mulai dengan header M3U tunggal
    combined_content = "#EXTM3U\n"
    
    with open(SOURCE_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        try:
            print(f"Mengambil: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Memproses konten dan menghapus header #EXTM3U dari setiap sumber
            lines = response.text.splitlines()
            content_without_header = "\n".join(line for line in lines if line.strip() and not line.strip().startswith("#EXTM3U"))
            combined_content += content_without_header + "\n"
        except Exception as e:
            print(f"Gagal mengambil {url}: {e}")
            
    return combined_content

def save_playlist(content):
    """Menyimpan konten playlist akhir ke file output."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Playlist berhasil disimpan ke {OUTPUT_FILE}")

def save_last_update():
    """Menyimpan stempel waktu saat ini untuk melacak waktu pembaruan terakhir."""
    with open(LAST_UPDATE_FILE, "w") as f:
        f.write(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    print(f"last_update.txt berhasil dibuat di {LAST_UPDATE_FILE}")

if __name__ == "__main__":
    content = fetch_and_combine_sources()
    save_playlist(content)
    save_last_update()
    
