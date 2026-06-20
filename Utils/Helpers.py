from urllib.parse import urlparse, urlunparse, urldefrag, urljoin

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
    
class URLNormalizer:
    BLOCKED_EXTENSIONS={".pdf",".doc",".docx",".xls",".xlsx",".zip",".rar",".7z",".jpg",".jpeg",".png",".gif",".svg",".webp",".ico",".css",".js",".xml",".json",".mp4",".mp3",".wav",".avi",".mov",".woff",".woff2",".ttf",".eot"}
    @staticmethod
    def normalize(base_url:str,url:str)->str|None:
        if not url:
            return None
        url=urljoin(base_url,url.strip())
        url=urldefrag(url).url
        parsed=urlparse(url)
        clean=f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        lower=clean.lower()
        for ext in URLNormalizer.BLOCKED_EXTENSIONS:
            if lower.endswith(ext):
                return None
        return clean.rstrip("/") or clean