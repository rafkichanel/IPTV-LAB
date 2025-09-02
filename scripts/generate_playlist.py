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
    """Fetches M3U content from all URLs in sources.txt and combines it."""
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
            print(f"Gagal ambil {url}: {e}")
    return combined_content

def parse_and_deduplicate(content):
    """
    Parses M3U content, removes duplicate channels, and formats the output.
    A channel is considered a duplicate if its name is the same as one already seen.
    """
    lines = content.split('\n')
    seen_channels = set()
    unique_content = ["#EXTM3U"]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        # Check for the start of a new channel entry
        if line.startswith('#EXTINF'):
            # The channel name is after the last comma
            match = re.search(r',(.+)$', line)
            if match:
                channel_name = match.group(1).strip()
                # Check if we have seen this channel before
                if channel_name not in seen_channels:
                    # If not, add its info and URL to the unique list
                    seen_channels.add(channel_name)
                    unique_content.append(line)
                    # The URL is on the next line
                    if i + 1 < len(lines):
                        unique_content.append(lines[i+1])
                    i += 2  # Move to the next potential channel entry
                else:
                    # If it's a duplicate, skip both lines
                    i += 2
            else:
                # If there's no channel name, just move on
                i += 1
        else:
            # For any other line (like #EXTM3U), just skip it if it's not the first line
            i += 1
            
    return "\n".join(unique_content)

def save_playlist(content):
    """Saves the final playlist content to the output file."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Playlist berhasil disimpan ke {OUTPUT_FILE}")

def save_last_update():
    """Saves the current timestamp to track the last update time."""
    with open(LAST_UPDATE_FILE, "w") as f:
        f.write(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    print(f"last_update.txt berhasil dibuat di {LAST_UPDATE_FILE}")

if __name__ == "__main__":
    combined_raw_content = fetch_and_combine_sources()
    deduplicated_content = parse_and_deduplicate(combined_raw_content)
    save_playlist(deduplicated_content)
    save_last_update()
        
