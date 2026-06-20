import asyncio
from urllib.parse import urlparse
from Checks.Reachability.HTTPStatus import HTTPStatus
from Checks.Reachability.DNS import DNS
from Checks.Reachability.SSL import SSL
from Checks.Reachability.Robots import Robots
from Checks.Reachability.Sitemap import Sitemap
from Checks.Reachability.Speed import Speed
from Utils.Helpers import URLHandler

class HealthCheck:
    @staticmethod
    async def run(url: str) -> dict:

        url = URLHandler.ensure_https(url=url)
        
        http, dns, ssl, robots, sitemap, speed = await asyncio.gather(
            HTTPStatus.run(url),
            DNS.run(URLHandler.strip_https(url=url)),
            SSL.run(URLHandler.strip_https(url=url)),
            Robots.run(url),
            Sitemap.run(url),
            Speed.run(url),
            return_exceptions=True
        )
        
        # Explicit exception formatting check for safe dictionary reading
        results = [http, dns, ssl, robots, sitemap, speed]
        for idx, res in enumerate(results):
            if isinstance(res, Exception):
                results[idx] = {"success": False, "data": None, "error": f"Task execution unhandled failure: {str(res)}"}
        
        http, dns, ssl, robots, sitemap, speed = results
        reachable = bool(http.get("success") and dns.get("success"))
        
        return {
            "reachable": reachable,
            "domain": url,
            "http": http,
            "dns": dns,
            "ssl": ssl,
            "robots": robots,
            "sitemap": sitemap,
            "speed": speed
        }

if __name__ == "__main__":
    async def main():
        ans = await HealthCheck.run("https://google.com")
        print(ans)
    asyncio.run(main())