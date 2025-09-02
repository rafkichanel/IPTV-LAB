import requests
import os
from datetime import datetime
import re

# Lokasi file sumber dan hasil
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder scripts
SOURCE_FILE = os.path.join(BASE_DIR, "sources.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "Finalplay.m3u")
LAST_UPDATE_FILE = os.path.join(BASE_DIR, "last_update.txt")

def fetch_and_combine_sources():
    """Mengambil konten M3U dari semua URL di sources.txt dan menggabungkannya."""
    combined_content = ""
    with open(SOURCE_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        try:
            print(f"Mengambil: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            combined_content += response.text.strip() + "\n"
        except Exception as e:
            print(f"Gagal mengambil {url}: {e}")
    return combined_content

def parse_and_deduplicate(content):
    """
    Memproses konten M3U, menghapus saluran ganda, dan menyimpan semua baris unik.
    """
    lines = content.split('\n')
    seen_channels = set()
    unique_content = ["#EXTM3U"] # Mulai dengan satu header utama
    
    i = 0
    while i < len(lines):
        line = lines[i]
        # Jika baris adalah header, lewati kecuali yang pertama
        if line.strip() == "#EXTM3U":
            i += 1
            continue

        # Periksa awal dari entri saluran baru
        if line.startswith('#EXTINF'):
            # Nama saluran berada setelah koma terakhir
            match = re.search(r',(.+)$', line)
            if match:
                channel_name = match.group(1).strip()
                if channel_name not in seen_channels:
                    seen_channels.add(channel_name)
                    unique_content.append(line)
                    # URL berada di baris berikutnya
                    if i + 1 < len(lines):
                        unique_content.append(lines[i+1])
                    i += 2  # Pindah ke entri saluran berikutnya
                else:
                    # Jika itu duplikat, lewati kedua baris tersebut
                    i += 2
            else:
                # Jika tidak ada nama saluran, lewati saja
                i += 1
        else:
            # Jika itu baris lain (seperti #EXTVLCOPT, komentar, dll), tambahkan langsung
            if line.strip(): # Pastikan bukan baris kosong
                unique_content.append(line)
            i += 1
            
    return "\n".join(unique_content)

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
    combined_raw_content = fetch_and_combine_sources()
    deduplicated_content = parse_and_deduplicate(combined_raw_content)
    save_playlist(deduplicated_content)
    save_last_update()
