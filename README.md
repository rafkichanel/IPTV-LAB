# 🎬 IPTV Lab

[![Auto Update IPTV](https://github.com/USERNAME/iptv-lab/actions/workflows/main.yml/badge.svg)](https://github.com/USERNAME/iptv-lab/actions/workflows/main.yml)

Repository ini digunakan untuk **eksperimen playlist IPTV**.  
Playlist diperbarui **otomatis setiap 6 jam** menggunakan GitHub Actions.

---

## 📂 File Penting
- `sources.txt` → daftar sumber playlist (link m3u)  
- `scripts/generate_playlist.py` → script generator playlist  
- `Finalplay.m3u` → hasil playlist yang sudah digabung & difilter  
- `last_update.txt` → catatan terakhir kali update  

---

## ⚡ Cara Kerja
1. GitHub Actions akan jalan tiap **6 jam** (`cron: "0 */6 * * *"`).  
2. Script Python akan:
   - Mengunduh semua link dari `sources.txt`  
   - Membersihkan channel duplikat  
   - Memfilter channel tertentu (sesuai aturan script)  
   - Menyimpan hasil akhir ke `Finalplay.m3u`  
3. Perubahan otomatis di-commit ke repo.

---

## ▶️ Cara Pakai
1. Copy link playlist berikut ke aplikasi IPTV favorit (misal: VLC, IPTV Smarters, Tivimate, dll):
