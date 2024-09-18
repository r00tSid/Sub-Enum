import asyncio
import requests
import dns.resolver
import argparse
import aiohttp
import pyfiglet
from colorama import Fore, init
import logging

# Initialize colorama and logging
init(autoreset=True)
logging.basicConfig(level=logging.INFO)

# ASCII Art Banner
banner = pyfiglet.figlet_format("SUB-ENUM", font="slant")
author_info = f"{Fore.CYAN}Created by https://github.com/r00tSid"

# Set up DNS resolver with a longer timeout
resolver = dns.resolver.Resolver()
resolver.timeout = 10
resolver.lifetime = 10
semaphore = asyncio.Semaphore(10)  # Limit the number of concurrent resolves

async def fetch_subdomains_from_crtsh(session, domain: str) -> set:
    subdomains = set()
    try:
        async with session.get(f"https://crt.sh/?q={domain}&output=json") as response:
            response.raise_for_status()  # Raise an error for bad responses
            certs = await response.json()
            for cert in certs:
                subdomain = cert['name_value'].strip().strip('.')
                if subdomain.endswith(domain):
                    subdomains.add(subdomain)
    except Exception as e:
        logging.error(f"Error fetching from crt.sh: {e}")
    return subdomains

def generate_subdomains(domain: str) -> set:
    common_subdomains = ['www', 'mail', 'dev', 'test', 'api', 'blog', 'shop', 'app']
    return {f"{sub}.{domain}" for sub in common_subdomains}

async def resolve_subdomain(subdomain: str) -> tuple:
    if len(subdomain) > 255:
        logging.warning(f"Skipping {subdomain}: A DNS name is > 255 octets long.")
        return subdomain, None

    async with semaphore:
        for _ in range(3):  # Retry mechanism
            try:
                answers = await asyncio.get_event_loop().run_in_executor(None, resolver.resolve, subdomain, 'A')
                return subdomain, [ip.address for ip in answers]
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                return subdomain, None
            except Exception as e:
                logging.error(f"Error resolving {subdomain}: {e}")
                await asyncio.sleep(1)  # Wait a bit before retrying
    return subdomain, None

async def main(domains: list, output_file: str):
    all_subdomains = set()
    
    async with aiohttp.ClientSession() as session:
        fetch_tasks = [fetch_subdomains_from_crtsh(session, domain) for domain in domains]
        results = await asyncio.gather(*fetch_tasks)
        
        for subdomains in results:
            all_subdomains.update(subdomains)
        
        generated_subs = {sub for domain in domains for sub in generate_subdomains(domain)}
        all_subdomains.update(generated_subs)
        
        resolved_subdomains = {}
        resolve_tasks = [resolve_subdomain(sub) for sub in all_subdomains]
        resolved_results = await asyncio.gather(*resolve_tasks)

        for resolved in resolved_results:
            if resolved[1]:  # If there are IPs resolved
                resolved_subdomains[resolved[0]] = resolved[1]
            else:
                logging.warning(f"Failed to resolve {resolved[0]}")

    if resolved_subdomains:
        print(f"\n{Fore.GREEN}Resolved Subdomains:")
        for subdomain, ips in resolved_subdomains.items():
            output_line = f"{Fore.YELLOW}{subdomain}: {', '.join(ips)}"
            print(output_line)
            if output_file:
                with open(output_file, 'a') as f:
                    f.write(f"{subdomain}: {', '.join(ips)}\n")
    else:
        print(f"{Fore.RED}No subdomains were resolved.")

if __name__ == "__main__":
    print(Fore.MAGENTA + banner)
    print(author_info)

    parser = argparse.ArgumentParser(description="Subdomain Enumeration Tool")
    parser.add_argument("-d", "--domain", help="Single domain to enumerate subdomains for")
    parser.add_argument("-dL", "--domain-list", help="File containing list of domains to enumerate subdomains for")
    parser.add_argument("-o", "--output", help="File to store resolved subdomains")
    args = parser.parse_args()

    domains = []
    if args.domain:
        domains = [args.domain]
    elif args.domain_list:
        with open(args.domain_list, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
    else:
        print(f"{Fore.RED}Error: You must specify a domain or a list of domains. Use -h for help.")
    
    if domains:
        asyncio.run(main(domains, args.output))
