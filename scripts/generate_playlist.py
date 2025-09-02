import requests
import os
import re
from datetime import datetime

# Lokasi file sumber dan hasil
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = os.path.join(BASE_DIR, "sources.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "Finalplay.m3u")

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
            print(f"📡 Mengunduh dari sumber: {url}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            # Memproses konten dan menghapus header #EXTM3U dari setiap sumber
            lines = response.text.splitlines()
            content_without_header = "\n".join(line for line in lines if line.strip() and not line.strip().startswith("#EXTM3U"))
            
            # --- Terapkan semua filter yang sudah ada ---
            cleaned_lines = []
            for line in content_without_header.splitlines():
                # Filter 'WHATSAPP'
                if "WHATSAPP" in line.upper():
                    continue
                # Menghapus logo
                if line.startswith("#EXTINF"):
                    line = re.sub(r'tvg-logo="[^"]*"', '', line)
                    line = re.sub(r'group-logo="[^"]*"', '', line)
                cleaned_lines.append(line)
            
            # Tambahkan ke konten gabungan
            combined_content += "\n".join(cleaned_lines) + "\n"
        except requests.exceptions.RequestException as e:
            print(f"❗ Gagal mengambil data dari {url}: {e}")
        except Exception as e:
            print(f"❌ Terjadi kesalahan tak terduga: {e}")
            
    return combined_content

def save_and_process_playlist(content):
    """Memproses dan menyimpan konten playlist akhir ke file output."""
    if not content:
        print("Tidak ada konten untuk disimpan.")
        return False
        
    try:
        lines = content.splitlines()
        
        # --- Mengurutkan channel Live Event ---
        live_event = []
        other_channels = []
        current_group = None
        
        for line in lines:
            if line.startswith("#EXTINF"):
                match = re.search(r'group-title="([^"]+)"', line)
                if match:
                    current_group = match.group(1)
                
                # Mengubah nama grup 'SEDANG LIVE' menjadi 'LIVE EVENT'
                if current_group and current_group.upper() == "SEDANG LIVE":
                    line = line.replace('group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"')
                    current_group = "LIVE EVENT"

                if current_group and current_group.upper() == "LIVE EVENT":
                    live_event.append(line)
                else:
                    other_channels.append(line)
            else:
                if current_group and current_group.upper() == "LIVE EVENT":
                    live_event.append(line)
                else:
                    other_channels.append(line)
                    
        final_playlist = ["#EXTM3U"]
        final_playlist += live_event + other_channels

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(final_playlist))
            
        print(f"✅ Playlist diperbarui dan disimpan ke {OUTPUT_FILE} - {datetime.utcnow().isoformat()} UTC")
        return True
    except Exception as e:
        print(f"❌ Gagal menyimpan file: {e}")
        return False

# --- Jalankan proses ---
if __name__ == "__main__":
    print("Memulai proses pembuatan playlist...")
    final_content = fetch_and_combine_sources()
    if final_content:
        save_and_process_playlist(final_content)
    print("Proses selesai.")
