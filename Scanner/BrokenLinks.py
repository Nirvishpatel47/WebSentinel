#!/usr/bin/env python3
import asyncio
import httpx
from typing import Dict, List

class BrokenLinkValidator:
    def __init__(self, concurrency: int = 20, timeout: int = 10):
        self.concurrency = concurrency
        self.timeout = timeout

    async def _probe(self, client: httpx.AsyncClient, url: str) -> dict:
        try:
            res = await client.get(url, timeout=self.timeout, follow_redirects=True)
            return {"url": url, "http_code": res.status_code, "status": "OK" if res.status_code < 400 else "BROKEN"}
        except httpx.TimeoutException:
            return {"url": url, "http_code": None, "status": "TIMEOUT"}
        except Exception as e:
            return {"url": url, "http_code": None, "status": "FAILED"}

    async def validate_all(self, resource_map: Dict[str, dict]) -> List[dict]:
        print(f"\n🔍 Starting Async Asset Validation Engine across {len(resource_map)} items...")
        results = []
        queue = asyncio.Queue()
        
        for url in resource_map.keys():
            await queue.put(url)

        async def worker(client):
            while True:
                url = await queue.get()
                res = await self._probe(client, url)
                res["found_on"] = resource_map[url]["found_on"]
                res["resource_type"] = resource_map[url]["resource_type"]
                results.append(res)
                queue.task_done()

        async with httpx.AsyncClient(follow_redirects=True) as client:
            workers = [asyncio.create_task(worker(client)) for _ in range(self.concurrency)]
            await queue.join()
            for _ in workers: _.cancel()
            
        return results