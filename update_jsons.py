import json
import re
import time
import urllib.request as rq
import urllib.error
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("A")


def simple(url):
    res = {}
    with rq.urlopen(url) as resp:
        dns = json.loads(resp.read())

    for serv in dns["services"]:
        domains = serv[0]
        servers = serv[1]
        for d in domains:
            res[d] = servers
    return res


def main():
    whois = {}

    logger.info("Fetching root...\n")
    with rq.urlopen("https://www.iana.org/domains/root/db") as response:
        html = response.read().decode()
        domains = re.findall(r'href="(/domains/root/db/.*?\.html)">', html)

    total = len(domains)

    for i, d in enumerate(domains):
        domain = re.findall(r"db\/(.*?\.html)", d)[0].strip("/").split(".")[0]
        logger.info(f"{domain} ({i + 1} of {total})")

        while True:
            time.sleep(1)
            try:
                logger.info("Fetching domain registry...")
                with rq.urlopen("https://www.iana.org" + d) as resp:
                    html = resp.read().decode()
                break
            except urllib.error.HTTPError as e:
                logger.error(f"{str(e)} // Retrying...")
        w = re.search(r"WHOIS.*?<\/b>\s(.*?)\s", html)
        if w:
            w = whois[domain] = w.group(1)
        logger.info(f"WHOIS: {w}\n")

    with open("whois.json", "w") as f:
        whois = dict(sorted(whois.items()))
        with open("whois_sld.json") as s:
            whois.update(json.load(s))
        json.dump(whois, f, indent=4)
    logger.info("WHOIS dumped.")

    logger.info("Getting RDAP Bootstrap DNS...")
    with open("rdap.json", "w") as f:
        json.dump(simple("https://data.iana.org/rdap/dns.json"))

    logger.info("Getting RDAP Bootstrap IPv4...")
    with open("ipv4.json", "w") as f:
        json.dump(simple("https://data.iana.org/rdap/ipv4.json"))

    logger.info("Getting RDAP Bootstrap IPv6...")
    with open("ipv6.json", "w") as f:
        json.dump(simple("https://data.iana.org/rdap/ipv6.json"))

    logger.info("Getting RDAP Bootstrap ASNs...")
    with rq.urlopen("https://data.iana.org/rdap/asn.json") as response:
        asns = json.loads(response.read())["services"]
    res = {}
    for asn in asns:
        nums, servs = asn
        for n in nums:
            for x in range(*map(int, n.split("-"))):
                res[str(x)] = servs
    res = dict(sorted(res.items(), key=lambda item: int(item[0])))
    with open("asns.json", "w") as f:
        json.dump(res, f)
    logger.info("Done.")

main()
