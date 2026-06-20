import httpx
import time

class Speed:
    @staticmethod
    async def run(url: str) -> dict:
        """ Works with https:// or http:// """
        try:
            async with httpx.AsyncClient(timeout=20, http2=True, follow_redirects=True) as client:
                start = time.perf_counter()
                response = await client.get(url)
                total_ms = round((time.perf_counter() - start) * 1000, 2)
                ttfb_ms = round(response.elapsed.total_seconds() * 1000, 2)
                return {
                    "success": True,
                    "data": {
                        "status_code": response.status_code,
                        "ttfb_ms": ttfb_ms,
                        "total_ms": total_ms,
                        "redirect_history": [str(r.url) for r in response.history]
                    },
                    "error": None
                }
        except httpx.HTTPError as e:
            return {"success": False, "data": None, "error": f"HTTP network error: {type(e).__name__}"}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}

if __name__ == "__main__":
    import asyncio
    async def main():
        ans = await Speed.run("https://google.com")
        print(ans)
    asyncio.run(main())