import httpx
import re
import urllib.parse
import asyncio

async def test():
    query = 'site:instagram.com "Bezerra Advogados" Mogi das Cruzes'
    url = "https://lite.duckduckgo.com/lite/"
    data = {"q": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(url, data=data, headers=headers)
        print(f"Status Lite: {res.status_code}")
        
        matches = re.findall(r'href=[\'"]([^\'"]+)[\'"]', res.text)
        candidates = []
        for decoded in matches:
            if "?uddg=" in decoded:
                decoded = urllib.parse.unquote(decoded.split("?uddg=")[1])
            if "instagram.com" in decoded:
                parts = decoded.split("instagram.com/")
                if len(parts) > 1:
                    username = parts[1].split("/")[0].split("?")[0].strip()
                    if username and username not in candidates and username not in ["about", "legal", "developer", "accounts", "p", "reel", "explore"]:
                        candidates.append(username)
        print("Candidates DDG Lite:")
        print(candidates[:10])

if __name__ == '__main__':
    asyncio.run(test())
