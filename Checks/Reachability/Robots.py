import httpx

class Robots:
    @staticmethod
    async def run(url: str) -> dict:
        """ works with https:// or http://  """
        try:
            target = url.rstrip("/") + "/robots.txt"
            async with httpx.AsyncClient(timeout=10, http2=True, follow_redirects=True) as client:
                response = await client.get(target)
                is_success = response.status_code == 200
                return {
                    "success": True, 
                    "data": {
                        "exists": is_success, 
                        "status_code": response.status_code,
                        "content": response.text if is_success else None
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
        ans = await Robots.run("https://google.com")
        print(ans)
    asyncio.run(main())