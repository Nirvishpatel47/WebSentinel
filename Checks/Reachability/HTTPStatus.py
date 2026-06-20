import httpx

class HTTPStatus:
    @staticmethod
    async def run(url: str) -> dict:
        """ Needs https:// or http:// """
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=15, http2=True) as client:
                response = await client.get(url)
                return {"success":True, "data":{"url":url, "status_code":response.status_code, "final_url":str(response.url), "response_time_ms":round(response.elapsed.total_seconds()*1000,2)}, "error":None}
        except Exception as e:
            return {"success":False, "data":None, "error":str(e)}

if __name__ == "__main__":
    import asyncio
    async def main():
        ans = await HTTPStatus.run("https://google.com")
        print(ans)
    asyncio.run(main())