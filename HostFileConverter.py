#!/usr/bin/env python

__author__ = 'balles'

import glob
import os


# sources must be manually downloaded cause automation is forbidden by most services
# http://winhelp2002.mvps.org/hosts.txt
# http://hosts-file.net/download/hosts.txt
# http://pgl.yoyo.org/adservers/serverlist.php?hostformat=dnsmasq&showintro=0&mimetype=plaintext
# http://someonewhocares.org/hosts/hosts


# Some input hosts files are a bit too restrictive. So the entries in this list won't be
# included in the output file
url_filter = [
    "no-ip.com",
    "www.no-ip.com",
    "blogspot.com",
    "s3.amazonaws.com",
    "jdownloader.org",
    "www.jdownloader.org"
]



def write_output(file, domains, output_format):
    for domain in domains:
        file.write(output_format(domain))


def main():
    print os.getcwd()
    files = glob.glob(os.path.join(os.getcwd(), '*.hosts'))
    lines_overall = 0
    domains = set()

    for filename in files:
        lines_per_file = 0
        relevant_lines_per_file = 0
        splited_lines = 0
        unfiltered_urls = 0
        with open(filename, 'r') as f:
            for line in f:
                lines_per_file += 1
                if (not line.startswith('#') and len(line) > 0 and
                    not line.isspace()):
                    relevant_lines_per_file += 1
                    parts = line.split()
                    if len(parts) > 1:
                        splited_lines += 1
                        url = parts[1]
                        if url not in url_filter:
                            unfiltered_urls += 1
                            domains.add(url)

            print "file: " + filename + " has " + str(lines_per_file) +\
                  "lines, relevant: " + str(relevant_lines_per_file) + \
                  " splited: " + str(splited_lines) + " unfiltered lines " +\
                  str(unfiltered_urls)
            lines_overall += lines_per_file
            f.close()

    print 'overall line count ' + str(lines_overall)
    print "unique unfiltered domains: ", len(domains)

    dnsmasq = 'address=/{0}/127.0.0.1\n'.format
    hosts = '127.0.0.1 {0}\n'.format

    with open(os.path.join(os.getcwd(), 'hosts.out'), 'w') as output_file:
        write_output(output_file, domains, dnsmasq)
        output_file.close()


if __name__ == '__main__':
    main()

