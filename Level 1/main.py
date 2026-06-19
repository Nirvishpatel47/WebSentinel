# health_monitor.py

import asyncio
from urllib.parse import urlparse

from Health_Checker.dns_check import check_dns
from Health_Checker.Reachability import WebsiteChecker
from Health_Checker.robots_check import check_discovery
from Health_Checker.ssl_checker import check_ssl

from urllib.parse import urlparse


def normalize_url(url: str) -> str:
    url = url.strip()

    if not url.startswith(
        ("http://", "https://")
    ):
        url = f"https://{url}"

    return url

class HealthMonitor:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.http_checker = WebsiteChecker()
        return cls._instance

    @staticmethod
    def _extract_domain(url: str) -> str:
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        parsed = urlparse(url)
        return parsed.hostname

    async def check(self, url: str) -> dict:
        url = normalize_url(url)
        domain = self._extract_domain(url)
        http_task = self.http_checker.check(url)
        dns_task = asyncio.to_thread( check_dns, domain )
        ssl_task = asyncio.to_thread( check_ssl, domain )
        discovery_task = check_discovery( self.http_checker, url )
        http_result, dns_result, ssl_result, discovery_result = (
            await asyncio.gather(
                http_task,
                dns_task,
                ssl_task,
                discovery_task,
                return_exceptions=True
            )
        )

        return {
            "website": domain,

            "http": (
                http_result
                if not isinstance(http_result, Exception)
                else {
                    "error": str(http_result)
                }
            ),

            "dns": (
                dns_result
                if not isinstance(dns_result, Exception)
                else {
                    "error": str(dns_result)
                }
            ),

            "ssl": (
                ssl_result
                if not isinstance(ssl_result, Exception)
                else {
                    "error": str(ssl_result)
                }
            ),

            "discovery": (
                discovery_result
                if not isinstance(discovery_result, Exception)
                else {
                    "error": str(discovery_result)
                }
            )
        }

    async def close(self):
        await self.http_checker.close()

import asyncio


async def main():
    monitor = HealthMonitor()

    result = await monitor.check(
        "spreadme.institute"
    )

    print(result)

    await monitor.close()


asyncio.run(main())