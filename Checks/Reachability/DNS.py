import asyncio
import dns.resolver

class DNS:
    @staticmethod
    async def run(domain: str) -> dict:
        """ Do not need https:// or http:// """
        try:
            resolver = dns.resolver.Resolver()
            a_records=await asyncio.to_thread(lambda:[str(r) for r in resolver.resolve(domain,"A")])
            try: 
                aaaa_records=await asyncio.to_thread(lambda:[str(r) for r in resolver.resolve(domain,"AAAA")])
            except:
                aaaa_records=[]
            return {"success": True, "data":{"domain" :domain, "a_records": a_records, "aaaa_records" :aaaa_records}, "error": None}
        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
        
if __name__ == "__main__":
    import asyncio
    async def main():
        ans = await DNS.run("google.com")
        print(ans)
    asyncio.run(main())