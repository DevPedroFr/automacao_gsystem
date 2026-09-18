import asyncio
import os
import sys

sys.path.append(os.path.abspath('backend_python'))
from app.integrations.search import DuckDuckGoSearch

async def test():
    candidates = await DuckDuckGoSearch.search_instagram_profiles("Bezerra Advogados", "Mogi das Cruzes")
    print(f"Candidates: {candidates}")

if __name__ == '__main__':
    asyncio.run(test())
