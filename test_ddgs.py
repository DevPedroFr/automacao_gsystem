from duckduckgo_search import DDGS

def test():
    query = 'site:instagram.com "Bezerra Advogados" Mogi das Cruzes'
    candidates = []
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=10)
        for r in results:
            url = r.get("href", "")
            if "instagram.com" in url:
                parts = url.split("instagram.com/")
                if len(parts) > 1:
                    username = parts[1].split("/")[0].split("?")[0].strip()
                    if username and username not in candidates and username not in ["about", "legal", "developer", "accounts", "p", "reel", "explore"]:
                        candidates.append(username)
    except Exception as e:
        print(f"Error: {e}")
        
    print(f"Candidates DDGS: {candidates}")

if __name__ == '__main__':
    test()
