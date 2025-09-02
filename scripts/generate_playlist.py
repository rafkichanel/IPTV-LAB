import requests
import os
import re
from datetime import datetime

# URL sumber M3U yang ingin Anda gunakan (ubah ini sesuai kebutuhan)
SOURCE_URL = "https://iptv-org.github.io/iptv/index.m3u"

# Lokasi file output
# Skrip akan membuat Finalplay.m3u di folder yang sama dengan skrip ini
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Finalplay.m3u")

def process_single_playlist(source_url, output_file):
    """
    Mengunduh, memproses, dan menyimpan playlist dari satu URL sumber.
    """
    try:
        print(f"📡 Mengunduh dari sumber: {source_url}")
        r = requests.get(source_url, timeout=15)
        r.raise_for_status()
        lines = r.text.splitlines()

        # --- Filter di awal (dipertahankan) ---
        # Menghapus baris yang berkaitan dengan "WHATSAPP"
        lines = [line for line in lines if "WHATSAPP" not in line.upper()]
        
        # --- Logika penghapusan logo UNIVERSAL ---
        cleaned_lines = []
        for line in lines:
            if line.startswith("#EXTINF"):
                line = re.sub(r'tvg-logo="[^"]*"', '', line)
                line = re.sub(r'group-logo="[^"]*"', '', line)
                cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        lines = cleaned_lines
        
        playlist_content = "\n".join(lines)
        playlist_content = re.sub(r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', playlist_content, flags=re.IGNORECASE)

        lines = playlist_content.splitlines()
        live_event = []
        other_channels = []
        current_group = None

        for line in lines:
            if line.startswith("#EXTINF"):
                match = re.search(r'group-title="([^"]+)"', line)
                if match:
                    current_group = match.group(1)
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

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_playlist))
        
        print(f"✅ Playlist diperbarui dan disimpan ke {output_file} - {datetime.utcnow().isoformat()} UTC")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"❗ Gagal mengambil data dari {source_url}: {e}")
        return False
    except Exception as e:
        print(f"❌ Terjadi kesalahan tak terduga: {e}")
        return False

# --- Jalankan proses ---
if __name__ == "__main__":
    process_single_playlist(SOURCE_URL, OUTPUT_FILE)
