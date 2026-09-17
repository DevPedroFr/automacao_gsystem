import re
import urllib.parse
from typing import List
import httpx

class DuckDuckGoSearch:
    @staticmethod
    async def search_instagram_profiles(company_name: str, city: str = "") -> List[str]:
        query = f'site:instagram.com "{company_name}" {city}'.strip()
        url = "https://html.duckduckgo.com/html/"
        data = {"q": query}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, data=data, headers=headers)
                res.raise_for_status()
                html = res.text
                
                candidates = []
                matches = re.findall(r'href=[\'"]//duckduckgo\.com/l/\?uddg=([^\'"]+)[\'"]', html)
                
                for m in matches:
                    decoded = urllib.parse.unquote(m)
                    if "instagram.com" in decoded:
                        if "/p/" in decoded or "/reel/" in decoded or "/explore/" in decoded or "/tags/" in decoded or "/stories/" in decoded:
                            continue
                        
                        parts = decoded.split("instagram.com/")
                        if len(parts) > 1:
                            username = parts[1].split("/")[0].split("?")[0].strip()
                            if username and username not in candidates and username != "about" and username != "legal" and username != "developer":
                                candidates.append(username)
                                
                        if len(candidates) >= 5:
                            break
                            
                return candidates
        except Exception as e:
            print(f"Error searching DDG: {e}")
            return []
