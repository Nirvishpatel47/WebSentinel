import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


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

    # -----------------------------
    # Check robots.txt
    # -----------------------------
    try:
        robots_url = f"{base_url.rstrip('/')}/robots.txt"

        response = await self._client.get(
            robots_url
        )

        robots_text = response.text

        robots_valid = (
            response.status_code == 200
            and "user-agent" in robots_text.lower()
        )

        result["robots"] = {
            "exists": response.status_code == 200,
            "valid": robots_valid,
            "status_code": response.status_code,
            "size": len(robots_text),
        }

        if robots_valid:
            for line in robots_text.splitlines():

                line = line.strip()

                if line.lower().startswith(
                    "sitemap:"
                ):
                    sitemap_url = (
                        line.split(":", 1)[1]
                        .strip()
                    )

                    if sitemap_url:
                        discovered_sitemaps.add(
                            sitemap_url
                        )

    except Exception as e:
        logger.exception(
            "robots.txt check failed for %s",
            base_url
        )

        result["robots"]["error"] = (
            type(e).__name__
        )

    # -----------------------------
    # Fallback sitemap.xml
    # -----------------------------
    if not discovered_sitemaps:
        discovered_sitemaps.add(
            f"{base_url.rstrip('/')}/sitemap.xml"
        )

    # -----------------------------
    # Validate every sitemap
    # -----------------------------
    for sitemap_url in discovered_sitemaps:

        sitemap_result = {
            "url": sitemap_url,
            "exists": False,
            "valid": False,
            "status_code": None,
            "type": None,
        }

        try:
            response = await self._client.get(
                sitemap_url
            )

            sitemap_result["status_code"] = (
                response.status_code
            )

            if response.status_code != 200:
                result["sitemaps"].append(
                    sitemap_result
                )
                continue

            content_type = (
                response.headers.get(
                    "content-type",
                    ""
                ).lower()
            )

            # XML expected
            if "xml" not in content_type:
                sitemap_result[
                    "error"
                ] = (
                    f"unexpected_content_type:"
                    f" {content_type}"
                )

                result["sitemaps"].append(
                    sitemap_result
                )
                continue

            try:
                root = ET.fromstring(
                    response.text
                )

                root_tag = (
                    root.tag.split("}")[-1]
                )

                valid_root = root_tag in (
                    "urlset",
                    "sitemapindex"
                )

                sitemap_result.update(
                    {
                        "exists": True,
                        "valid": valid_root,
                        "type": root_tag,
                    }
                )

            except ET.ParseError:
                sitemap_result[
                    "error"
                ] = "invalid_xml"

        except Exception as e:
            logger.exception(
                "sitemap validation failed: %s",
                sitemap_url
            )

            sitemap_result[
                "error"
            ] = type(e).__name__

        result["sitemaps"].append(
            sitemap_result
        )

    return result

if __name__ == "__main__":
    import asyncio
    async def main():
        ans = await check_discovery