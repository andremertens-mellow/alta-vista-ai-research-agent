"""
Script para testar o coletor RSS.
"""
import asyncio, urllib.parse
from collections import Counter
from src.collectors.rss_collector import fetch_all

async def main():
    items = await fetch_all()
    domains = [urllib.parse.urlparse(it["link"]).netloc for it in items]
    print("Total por fonte:", Counter(domains))
    for it in items[:20]:     # imprime 20 para ver variedade
        print(f"[{it['published']}] {it['title']} — {it['link']}")

if __name__ == "__main__":
    asyncio.run(main())