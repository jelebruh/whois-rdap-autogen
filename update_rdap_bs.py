import json
import urllib.request as rq
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
    logger.info("Getting RDAP Bootstrap DNS...")
    with open("rdap.json", "w") as f:
        json.dump(simple("https://data.iana.org/rdap/dns.json"), f)

    logger.info("Getting RDAP Bootstrap IPv4...")
    with open("ipv4.json", "w") as f:
        json.dump(simple("https://data.iana.org/rdap/ipv4.json"), f)

    logger.info("Getting RDAP Bootstrap IPv6...")
    with open("ipv6.json", "w") as f:
        json.dump(simple("https://data.iana.org/rdap/ipv6.json"), f)

    logger.info("Getting RDAP Bootstrap ASNs...")
    with rq.urlopen("https://data.iana.org/rdap/asn.json") as response:
        asns = json.loads(response.read())["services"]
    res = []
    for asn in asns:
        nums, servs = asn
        for n in nums:
            tmp = []
            nr = n.split("-")
            tmp.append(list(nr))
        tmp.append(asn)
        res.append(tmp)
    with open("asns.json", "w") as f:
        json.dump(res, f)
    logger.info("Done.")

main()
