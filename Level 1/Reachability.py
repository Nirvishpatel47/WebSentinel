import time
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class WebsiteChecker:
    _client = httpx.AsyncClient(
        follow_redirects=True,
        timeout=15,
        verify=True,
        headers={
            "User-Agent":
            "WebsiteHealthMonitor/1.0"
        }
    )

    @staticmethod
    def normalize_url(url: str) -> str:
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    @staticmethod
    def analyze_html(html: str) -> dict:
        soup = BeautifulSoup( html, "html.parser" )
        title = soup.title
        return {
            "html_received": bool(html),
            "content_length": len(html),
            "title_present": title is not None,
            "title": (
                title.text.strip()
                if title
                else None
            ),
            "has_body": soup.body is not None,
        }

    async def check(self, url: str) -> dict:
        url = self.normalize_url(url)
        start = time.perf_counter()
        try:
            response = await self._client.get(url)
            response_time = round( (time.perf_counter() - start) * 1000 )
            result = {
                "reachable": True,
                "status": (
                    "UP"
                    if 200 <= response.status_code < 400
                    else "DOWN"
                ),
                "http_status": response.status_code,
                "response_time_ms": response_time,
                "final_url": str(response.url),
            }
            if "text/html" in response.headers.get( "content-type", "" ):
                result["homepage"] = ( self.analyze_html( response.text ) )
            return result

        except httpx.TimeoutException:
            return {
                "reachable": False,
                "status": "DOWN",
                "error": "timeout"
            }

        except httpx.ConnectError:
            return {
                "reachable": False,
                "status": "DOWN",
                "error": "connection_failed"
            }

        except httpx.HTTPError as e:
            return {
                "reachable": False,
                "status": "DOWN",
                "error": str(e)
            }

    async def check_discovery(self, base_url: str) -> dict:
        result = {
            "robots": {
                "exists": False,
                "valid": False,
                "status_code": None,
                "size": 0,
            },
            "sitemaps": []
        }

        discovered_sitemaps = set()
        try:
            robots_url = f"{base_url.rstrip('/')}/robots.txt"

            response = await self._client.get( robots_url )

            robots_text = response.text

            robots_valid = ( response.status_code == 200 and "user-agent" in robots_text.lower() )

            result["robots"] = {
                "exists": response.status_code == 200,
                "valid": robots_valid,
                "status_code": response.status_code,
                "size": len(robots_text),
            }

            if robots_valid:
                for line in robots_text.splitlines():
                    line = line.strip()
                    if line.lower().startswith( "sitemap:" ):
                        sitemap_url = ( line.split(":", 1)[1] .strip() )
                        if sitemap_url:
                            discovered_sitemaps.add(sitemap_url)

        except Exception as e:
            logger.exception( "robots.txt check failed for %s", base_url )

            result["robots"]["error"] = ( type(e).__name__ )
        if not discovered_sitemaps:
            discovered_sitemaps.add( f"{base_url.rstrip('/')}/sitemap.xml" )

        for sitemap_url in discovered_sitemaps:
            sitemap_result = {
                "url": sitemap_url,
                "exists": False,
                "valid": False,
                "status_code": None,
                "type": None,
            }

            try:
                response = await self._client.get( sitemap_url )
                sitemap_result["status_code"] = ( response.status_code )
                if response.status_code != 200:
                    result["sitemaps"].append( sitemap_result ) 
                    continue

                content_type = ( response.headers.get( "content-type", "" ).lower() )
                # XML expected
                if "xml" not in content_type:
                    sitemap_result[ "error" ] = ( f"unexpected_content_type:" f" {content_type}" )
                    result["sitemaps"].append( sitemap_result )
                    continue
                try:
                    root = ET.fromstring( response.text )
                    root_tag = ( root.tag.split("}")[-1] )
                    valid_root = root_tag in ( "urlset", "sitemapindex" )
                    sitemap_result.update(
                        {
                            "exists": True,
                            "valid": valid_root,
                            "type": root_tag,
                        }
                    )
                except ET.ParseError:
                    sitemap_result[ "error" ] = "invalid_xml"

            except Exception as e:
                logger.exception( "sitemap validation failed: %s", sitemap_url )
                sitemap_result[ "error" ] = type(e).__name__
            result["sitemaps"].append( sitemap_result )
        return result

    async def close(self):
        await self._client.aclose()

if __name__ == "__main__":
    import asyncio
    checker = WebsiteChecker()
    async def main():
        # result = await checker.check(
        #     "google.com"
        # )
        result = await checker.check_discovery(
            "https://google.com"
        )
        print(result)
        await checker.close()
    asyncio.run(main())