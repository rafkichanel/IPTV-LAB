import requests
import os
import re
from datetime import datetime

# Lokasi file sumber dan hasil
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = os.path.join(BASE_DIR, "sources.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "Finalplay.m3u")

def validate_stream(url):
    """Memvalidasi URL channel dengan mencoba koneksi."""
    try:
        # Menggunakan HEAD request untuk efisiensi
        response = requests.head(url, timeout=5)
        # Atau GET request dengan stream=True untuk memeriksa koneksi awal
        # response = requests.get(url, timeout=5, stream=True)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False
    except Exception:
        return False

def fetch_and_combine_sources():
    """Mengambil konten M3U dari semua URL di sources.txt dan menggabungkannya."""
    unique_channels = {}
    
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
        return "#EXTM3U\n"

    for url in urls:
        try:
            print(f"📡 Mengunduh dari sumber: {url}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            lines = response.text.splitlines()
            for i in range(len(lines)):
                line = lines[i]
                if line.startswith("#EXTINF"):
                    if "WHATSAPP" in line.upper():
                        continue
                    
                    channel_name_match = re.search(r',(.+)', line)
                    if not channel_name_match:
                        continue
                    channel_name = channel_name_match.group(1).strip()
                    
                    if i + 1 < len(lines) and not lines[i+1].startswith('#'):
                        channel_url = lines[i+1]
                        
                        # Hanya tambahkan jika channel valid dan unik
                        if channel_name not in unique_channels:
                            print(f"   Memvalidasi {channel_name}...")
                            if validate_stream(channel_url):
                                filtered_line = re.sub(r'tvg-logo="[^"]*"', '', line)
                                filtered_line = re.sub(r'group-logo="[^"]*"', '', filtered_line)
                                unique_channels[channel_name] = f"{filtered_line}\n{channel_url}"
                                print(f"   ✅ {channel_name} valid.")
                            else:
                                print(f"   ❌ {channel_name} tidak valid.")
                            
        except requests.exceptions.RequestException as e:
            print(f"❗ Gagal mengambil data dari {url}: {e}")
        except Exception as e:
            print(f"❌ Terjadi kesalahan tak terduga: {e}")
    
    return "#EXTM3U\n" + "\n".join(unique_channels.values())

def save_and_process_playlist(content):
    """Memproses dan menyimpan konten playlist akhir ke file output."""
    if not content:
        print("Tidak ada konten untuk disimpan.")
        return False
        
    try:
        lines = content.splitlines()
        
        live_event = []
        other_channels = []
        current_group = None
        
        for line in lines:
            if line.startswith("#EXTINF"):
                match = re.search(r'group-title="([^"]+)"', line)
                if match:
                    current_group = match.group(1)
                
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

# Jalankan proses
if __name__ == "__main__":
    print("Memulai proses pembuatan playlist...")
    final_content = fetch_and_combine_sources()
    if final_content:
        save_and_process_playlist(final_content)
    print("Proses selesai.")
        
