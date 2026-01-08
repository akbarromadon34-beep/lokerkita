import requests
from bs4 import BeautifulSoup
import json
import time
import random
import hashlib
import os
import subprocess
from datetime import datetime

# ================= KONFIGURASI =================
OUTPUT_FILE = 'jobs.json'

# --- KONFIGURASI GITHUB ---
USE_GIT = True
# PERBAIKAN: Mengubah branch target menjadi 'master' sesuai log error Anda
GIT_BRANCH = "master" 
COMMIT_MESSAGE = f"Auto update lowongan: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

# ================= FUNGSI BANTUAN =================
def get_soup(url):
    try:
        time.sleep(random.uniform(2, 5)) # Delay diperlama sedikit agar aman
        print(f"Mengakses: {url} ...")
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"  [x] Gagal akses: {e}")
        return None

def generate_id(link):
    return int(hashlib.sha256(link.encode('utf-8')).hexdigest(), 16) % 10**8

def guess_category(title):
    title = title.lower()
    if "admin" in title: return "Admin"
    if "sales" in title or "marketing" in title: return "Marketing"
    if "it" in title or "developer" in title or "program" in title: return "Teknologi"
    if "design" in title or "kreatif" in title: return "Desain"
    if "accounting" in title or "keuangan" in title or "pajak" in title: return "Keuangan"
    if "guru" in title or "tutor" in title: return "Pendidikan"
    if "teknik" in title or "engineer" in title: return "Teknik"
    if "kesehatan" in title or "perawat" in title: return "Kesehatan"
    if "pabrik" in title or "produksi" in title or "operator" in title: return "Manufaktur"
    return "Umum"

# ================= SCRAPER 1: LOKERSEMAR.ID (UPDATE SELEKTOR) =================
def scrape_lokersemar():
    print("\n=== Memulai Scrape: LokerSemar.id ===")
    results = []
    base_url = "https://www.lokersemar.id/page/"
    
    for page in range(1, 3): 
        soup = get_soup(f"{base_url}{page}/")
        if not soup: continue
        
        # Cari semua elemen article atau div yang mungkin berisi post
        articles = soup.find_all('article')
        
        for item in articles:
            try:
                # Coba cari judul di h1, h2, atau h3
                title_elem = item.find('h2', class_='entry-title') or item.find('h1', class_='entry-title')
                if not title_elem: continue
                
                # Coba cari link di dalam judul
                link_elem = title_elem.find('a')
                if not link_elem: continue

                title = link_elem.text.strip()
                link = link_elem['href']
                
                results.append({
                    "id": generate_id(link),
                    "title": title,
                    "company": "Info LokerSemar",
                    "location": "Semarang",
                    "category": guess_category(title),
                    "salary": "Kompetitif",
                    "type": "Full Time",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "desc": "Info selengkapnya silakan klik tombol detail.",
                    "reqs": ["Cek link sumber untuk detail kualifikasi."],
                    "url": link,
                    "source": "LokerSemar"
                })
            except: continue
            
    print(f"  -> Berhasil mendapatkan {len(results)} data.")
    return results

# ================= SCRAPER 2: LOKER.ID (UPDATE SELEKTOR) =================
def scrape_loker_id():
    print("\n=== Memulai Scrape: Loker.id ===")
    results = []
    url = "https://www.loker.id/lokasi-pekerjaan/semarang" 
    
    soup = get_soup(url)
    if soup:
        # Loker.id kadang strukturnya berubah, kita cari container job-box
        job_cards = soup.select('.job-box') 
        if not job_cards: # Cadangan jika class berubah
            job_cards = soup.select('div[class*="job"]')

        for card in job_cards:
            try:
                # Cari judul: biasanya h3 atau h4 dengan link
                title_elem = card.select_one('h3 a') or card.select_one('h4 a')
                if not title_elem: continue
                
                title = title_elem.text.strip()
                link = title_elem['href']
                
                # Cari perusahaan
                company_elem = card.select_one('.company-name') or card.select_one('td:nth-of-type(2)')
                company = company_elem.text.strip() if company_elem else "Perusahaan"
                
                results.append({
                    "id": generate_id(link),
                    "title": title,
                    "company": company,
                    "location": "Semarang",
                    "category": guess_category(title),
                    "salary": "Nego",
                    "type": "Full Time",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "desc": "Lowongan kerja terbaru dari Loker.id",
                    "reqs": ["Kunjungi website sumber untuk melamar."],
                    "url": link,
                    "source": "Loker.id"
                })
            except Exception as e:
                continue
                
    print(f"  -> Berhasil mendapatkan {len(results)} data.")
    return results

# ================= SCRAPER 3: LOKERSEMARANG.COM (SUDAH OKE) =================
def scrape_lokersemarang_com():
    print("\n=== Memulai Scrape: LokerSemarang.com ===")
    results = []
    url = "https://www.lokersemarang.com/"
    
    soup = get_soup(url)
    if soup:
        posts = soup.select('article') 
        if not posts: posts = soup.select('.post')
        
        for post in posts:
            try:
                title_elem = post.select_one('h2 a') or post.select_one('h3 a')
                if not title_elem: continue
                
                title = title_elem.text.strip()
                link = title_elem['href']
                
                if "loker" not in link.lower() and "lowongan" not in link.lower() and "rekrutmen" not in link.lower():
                    continue

                results.append({
                    "id": generate_id(link),
                    "title": title,
                    "company": "Info LokerSemarang",
                    "location": "Semarang",
                    "category": guess_category(title),
                    "salary": "Kompetitif",
                    "type": "Full Time",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "desc": "Klik tombol detail untuk informasi lengkap.",
                    "reqs": ["Lihat detail selengkapnya."],
                    "url": link,
                    "source": "LokerSemarang.com"
                })
            except: continue

    print(f"  -> Berhasil mendapatkan {len(results)} data.")
    return results

# ================= FUNGSI UPDATE GITHUB (PERBAIKAN BRANCH) =================
def push_to_github():
    print(f"\n[GIT] Sedang mengirim update ke GitHub...")
    
    # 1. Cek folder .git
    if not os.path.exists(".git"):
        print("❌ ERROR: Folder ini belum terhubung ke Git/GitHub.")
        return

    try:
        # 2. Tambahkan file jobs.json
        subprocess.run(["git", "add", OUTPUT_FILE], check=True)
        
        # 3. Cek status apakah ada yang perlu di-commit
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            print("ℹ️ Tidak ada perubahan data baru. (Data di GitHub sudah sama dengan lokal)")
            return

        # 4. Commit
        print("-> Melakukan Commit...")
        subprocess.run(["git", "commit", "-m", COMMIT_MESSAGE], check=True)
        
        # 5. Push ke branch yang sesuai (Master)
        print(f"-> Melakukan Push ke origin/{GIT_BRANCH}...")
        subprocess.run(["git", "push", "origin", GIT_BRANCH], check=True)
        
        print("✅ SUKSES! Data berhasil di-push ke GitHub Pages.")
        print("Tunggu 1-3 menit hingga website terupdate.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Gagal melakukan perintah Git: {e}")
        print("Tips: Jika error 'rejected', coba ketik 'git pull origin master' dulu di terminal.")

# ================= MAIN PROGRAM =================
def main():
    all_jobs = []
    
    # Kumpulkan data
    try: all_jobs.extend(scrape_lokersemar())
    except Exception as e: print(f"Error LokerSemar: {e}")

    try: all_jobs.extend(scrape_loker_id())
    except Exception as e: print(f"Error Loker.id: {e}")

    try: all_jobs.extend(scrape_lokersemarang_com())
    except Exception as e: print(f"Error LokerSemarang.com: {e}")
    
    if not all_jobs:
        print("\n⚠️ PERINGATAN: Tidak ada data yang ditemukan dari semua sumber.")
        # Kita tetap lanjut agar bisa melihat data yang sudah ada sebelumnya (jika perlu logika merge)
        # Tapi di sini kita return saja agar tidak menimpa file dengan kosong
        return

    # Hapus duplikat & Simpan
    unique_jobs = {job['id']: job for job in all_jobs}.values()
    final_list = list(unique_jobs)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=4)
        
    print(f"\nTotal {len(final_list)} data tersimpan di '{OUTPUT_FILE}'.")

    if USE_GIT:
        push_to_github()

if __name__ == "__main__":
    main()