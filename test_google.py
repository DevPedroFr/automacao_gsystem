import httpx
import re
import urllib.parse
import asyncio

async def test():
    query = 'site:instagram.com "Bezerra Advogados" Mogi das Cruzes'
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9"
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        print(f"Status Google: {res.status_code}")
        matches = re.findall(r'href=[\'"](https?://[^\'"]+)[\'"]', res.text)
        # also search raw text
        matches += re.findall(r'https://www\.instagram\.com/([a-zA-Z0-9_\.]+)', res.text)
        
        candidates = []
        for decoded in matches:
            decoded = urllib.parse.unquote(decoded)
            if "instagram.com" in decoded:
                parts = decoded.split("instagram.com/")
                if len(parts) > 1:
                    username = parts[1].split("/")[0].split("?")[0].strip()
                    if username and username not in candidates and username not in ["about", "legal", "developer", "accounts", "p", "reel", "explore"]:
                        candidates.append(username)
            elif decoded and decoded not in candidates and decoded not in ["about", "legal", "developer", "accounts", "p", "reel", "explore"]:
                candidates.append(decoded)
        print("Candidates Google:")
        print(candidates[:10])

if __name__ == '__main__':
    asyncio.run(test())
