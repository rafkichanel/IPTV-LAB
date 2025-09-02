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
    
    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{SOURCE_FILE}' tidak ditemukan.")
        return None
    except Exception as e:
        print(f"Error saat membaca file sumber: {e}")
        return None

    if not urls:
        print("Peringatan: Tidak ada URL yang ditemukan di file sumber.")
        return combined_content

    for url in urls:
        try:
            print(f"Mengambil: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Memastikan respons HTTP OK (status 200)
            
            # Memproses konten dan menghapus header #EXTM3U dari setiap sumber
            lines = response.text.splitlines()
            content_without_header = "\n".join(line for line in lines if line.strip() and not line.strip().startswith("#EXTM3U"))
            combined_content += content_without_header + "\n"
        except requests.exceptions.RequestException as e:
            print(f"Gagal mengambil {url}: {e}")
        except Exception as e:
            print(f"Terjadi kesalahan tak terduga: {e}")
            
    return combined_content

def save_playlist(content):
    """Menyimpan konten playlist akhir ke file output dan mencatat waktu pembaruan."""
    if not content:
        print("Tidak ada konten untuk disimpan.")
        return False
        
    try:
        # Menulis konten ke file output
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Mencatat waktu pembaruan terakhir
        with open(LAST_UPDATE_FILE, "w") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
        print(f"File '{OUTPUT_FILE}' berhasil diperbarui.")
        return True
    except Exception as e:
        print(f"Gagal menyimpan file: {e}")
        return False

# Bagian utama skrip
if __name__ == "__main__":
    print("Memulai proses pembuatan playlist...")
    final_content = fetch_and_combine_sources()
    if final_content:
        save_playlist(final_content)
    print("Proses selesai.")

