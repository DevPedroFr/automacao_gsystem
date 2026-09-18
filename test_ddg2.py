import httpx
import re
import urllib.parse
import asyncio

async def test():
    query = 'site:instagram.com "Bezerra Advogados" Mogi das Cruzes'
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        print(f"Status: {res.status_code}")
        matches = re.findall(r'href=[\'"]([^\'"]+)[\'"]', res.text)
        candidates = []
        for decoded in matches:
            if "?uddg=" in decoded:
                decoded = urllib.parse.unquote(decoded.split("?uddg=")[1])
            if "instagram.com" in decoded:
                parts = decoded.split("instagram.com/")
                if len(parts) > 1:
                    username = parts[1].split("/")[0].split("?")[0].strip()
                    if username and username not in candidates and username not in ["about", "legal", "developer"]:
                        candidates.append(username)
        print("Candidates GET:")
        print(candidates)
        
        # Test Yahoo Search as fallback
        url2 = f"https://search.yahoo.com/search?p={urllib.parse.quote(query)}"
        res2 = await client.get(url2, headers=headers)
        print(f"Status Yahoo: {res2.status_code}")
        matches2 = re.findall(r'href=[\'"]([^\'"]+)[\'"]', res2.text)
        candidates2 = []
        for decoded in matches2:
            if "instagram.com" in decoded:
                parts = decoded.split("instagram.com/")
                if len(parts) > 1:
                    username = parts[1].split("/")[0].split("?")[0].strip()
                    username = urllib.parse.unquote(username)
                    if username and username not in candidates2 and username not in ["about", "legal", "developer", "accounts"]:
                        candidates2.append(username)
        print("Candidates Yahoo:")
        print(candidates2)

if __name__ == '__main__':
    asyncio.run(test())
