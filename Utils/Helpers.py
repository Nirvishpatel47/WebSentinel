from urllib.parse import urlparse, urlunparse

class URLHandler:

    @staticmethod
    def ensure_https(url: str) -> str:
        url = url.strip()
        if not url:
            return ""
        if "://" not in url:
            url = "https://" + url
        parsed = urlparse(url)
        if parsed.scheme != "https":
            parsed = parsed._replace(scheme="https")
        return urlunparse(parsed)
    
    @staticmethod
    def strip_https(url: str) -> str:
        url = url.strip()
        if "://" not in url:
            return url
        parsed = urlparse(url)
        if parsed.scheme in ("https", "http"):
            return urlunparse(parsed._replace(scheme="")).lstrip(":/")
        return url