import socket


def check_dns(domain: str) -> dict:
    try:
        infos = socket.getaddrinfo(
            domain,
            443,
            proto=socket.IPPROTO_TCP
        )

        ips = sorted({
            item[4][0]
            for item in infos
        })

        ipv4 = [
            ip
            for ip in ips
            if "." in ip
        ]

        ipv6 = [
            ip
            for ip in ips
            if ":" in ip
        ]

        return {
            "resolved": True,
            "ip_count": len(ips),
            "ipv4_count": len(ipv4),
            "ipv6_count": len(ipv6),
            "ips": ips
        }

    except socket.gaierror as e:
        return {
            "resolved": False,
            "error": "dns_resolution_failed",
            "details": str(e)
        }

    except Exception as e:
        return {
            "resolved": False,
            "error": type(e).__name__,
            "details": str(e)
        }

print(check_dns("google.com"))