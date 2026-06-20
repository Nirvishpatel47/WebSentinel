import ssl
import socket
import asyncio
from datetime import datetime,timezone

class SSL:
    @staticmethod
    async def run(domain: str) -> dict:
        """ Works without https:// or http:// """
        try:
            cert = await asyncio.to_thread(SSL._get_cert, domain)
            expires = datetime.strptime(cert["notAfter"],"%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
            days_remaining = (expires-datetime.now(timezone.utc)).days
            issuer = dict(x[0] for x in cert["issuer"]).get("organizationName")
            return {"success": True, "data": {"issuer": issuer, "expires": expires.isoformat(), "days_remaining": days_remaining, "valid": days_remaining>0} ,"error": None}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
        
    @staticmethod
    def _get_cert(domain):
        context = ssl.create_default_context()
        with socket.create_connection((domain,443),timeout=15) as sock:
            with context.wrap_socket(sock,server_hostname=domain) as ssock:
                return ssock.getpeercert()
            
if __name__ == "__main__":
    import asyncio
    async def main():
        ans = await SSL.run("google.com")
        print(ans)
    asyncio.run(main())