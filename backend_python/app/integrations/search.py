import asyncio
from typing import List

class DuckDuckGoSearch:
    @staticmethod
    async def search_instagram_profiles(company_name: str, city: str = "") -> List[str]:
        query = f'site:instagram.com "{company_name}" {city}'.strip()
        candidates = []
        try:
            from ddgs import DDGS
            def _sync_search():
                with DDGS() as ddgs:
                    return list(ddgs.text(query, max_results=10))
            
            results = await asyncio.to_thread(_sync_search)
            
            for r in results:
                url = r.get("href", "")
                if "instagram.com" in url:
                    parts = url.split("instagram.com/")
                    if len(parts) > 1:
                        username = parts[1].split("/")[0].split("?")[0].strip()
                        if username and username not in candidates and username not in ["about", "legal", "developer", "accounts", "p", "reel", "explore"]:
                            candidates.append(username)
                            if len(candidates) >= 5:
                                break
                                
            return candidates
        except Exception as e:
            print(f"Error searching DDG via ddgs library: {e}")
            return []
