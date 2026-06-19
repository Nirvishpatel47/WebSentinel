import ssl
import socket
from datetime import datetime, timezone
from urllib.parse import urlparse

def get_hostname(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return urlparse(url).hostname

def ssl_health(days_left):
    if days_left < 7:
        return "CRITICAL"

    if days_left < 30:
        return "WARNING"

    return "OK"

def check_ssl(domain: str):
    hostname = get_hostname(domain)
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
        expiry = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        
        san = [name for kind, name in cert.get("subjectAltName", []) if kind == "DNS"]
        
        issuer = dict(x[0] for x in cert["issuer"])
        subject = dict(x[0] for x in cert["subject"])

        days_left = (expiry - datetime.now(timezone.utc)).days

        return {
            "status": "success",
            "domain": hostname,
            "issued_to": subject.get("commonName"),
            "issuer": issuer.get("organizationName", issuer.get("commonName")),
            "expires_at": expiry.isoformat(), 
            "days_left": days_left,
            "san_list": san,
            "version": cert.get("version"),
            "SSL_Health": ssl_health(days_left)
        }
    except Exception as e:
        return {
            "status": "error",
            "domain": hostname,
            "message": str(e)
        }

if __name__ == "__main__":
    results = [check_ssl("google.com"), check_ssl("expired.badssl.com")]
    for res in results:
        print(res)