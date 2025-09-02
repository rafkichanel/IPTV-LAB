import requests
import re
from datetime import datetime

# File sumber (isi 1 URL playlist m3u)
SOURCE_FILE = "sources.txt"

# File output utama
OUTPUT_FILE = "Finalplay.m3u"


def fetch_and_clean(source_file):
    """
    Ambil playlist dari file sumber, bersihin duplikat & iklan.
    """
    channels = []
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]

        for idx, url in enumerate(urls, start=1):
            print(f"📡 Ambil sumber {idx}: {url}")
            try:
                r = requests.get(url, timeout=20)
                r.raise_for_status()
                lines = r.text.splitlines()

                cleaned = []
                for line in lines:
                    # hapus baris donasi/iklan tertentu
                    if any(word in line.upper() for word in ["WHATSAPP", "DONASI", "CONTACT ADMIN"]):
                        continue

                    if line.startswith("#EXTINF"):
                        # hapus logo universal
                        line = re.sub(r'tvg-logo="[^"]*"', '', line)
                        line = re.sub(r'group-logo="[^"]*"', '', line)
                        # normalisasi group-title
                        line = re.sub(r'group-title="SEDANG LIVE"', 'group-title="LIVE EVENT"', line, flags=re.IGNORECASE)
                        cleaned.append(line)
                    else:
                        cleaned.append(line)

                channels.extend(cleaned)
            except Exception as e:
                print(f"⚠️ Gagal ambil dari {url}: {e}")
    except FileNotFoundError:
        print(f"⚠️ File {source_file} tidak ditemukan.")
    return channels


def remove_duplicates(channels):
    """
    Hilangkan channel kembar berdasarkan nama (#EXTINF).
    """
    seen = set()
    unique = []
    current_info = None

    for line in channels:
        if line.startswith("#EXTINF"):
            channel_name = line.split(",")[-1].strip().lower()
            if channel_name in seen:
                current_info = None  # skip URL setelahnya
                continue
            seen.add(channel_name)
            current_info = line
            unique.append(line)
        else:
            if current_info:  # hanya simpan URL jika EXTINF tidak dibuang
                unique.append(line)
    return unique


def save_playlist(lines, output_file):
    """
    Simpan hasil playlist ke file .m3u
    """
    header = "#EXTM3U\n"
    content = header + "\n".join(lines)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Playlist berhasil disimpan: {output_file}")


def main():
    all_channels = fetch_and_clean(SOURCE_FILE)

    print(f"📊 Total channel sebelum filter: {len(all_channels)}")

    unique_channels = remove_duplicates(all_channels)
    print(f"📊 Total channel setelah filter duplikat: {len(unique_channels)}")

    save_playlist(unique_channels, OUTPUT_FILE)

    # log waktu update
    with open("last_update.txt", "w") as f:
        f.write(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    main()
