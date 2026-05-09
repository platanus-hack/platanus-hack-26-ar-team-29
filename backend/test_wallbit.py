import asyncio
import os
from dotenv import load_dotenv

from app.providers.wallbit.client import WallbitClient

load_dotenv()

async def main():
    api_key = os.getenv("WALLBIT_API_KEY")
    url = os.getenv("WALLBIT_MCP_URL", "https://api.wallbit.io")
    print(f"Using url: {url}")
    async with WallbitClient(api_key=api_key, base_url=url) as client:
        try:
            txs = await client._request("GET", "/transactions")
            import json
            print(json.dumps(txs, indent=2))
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
