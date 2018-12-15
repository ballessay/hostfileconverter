#!/usr/bin/env python

from __future__ import print_function

__author__ = 'ballessay'

from glob import glob
import os
import sys
import getopt

################################################################################
# sources must be manually downloaded cause automation is forbidden by most
# of the services
#
# http://winhelp2002.mvps.org/hosts.txt
# http://hosts-file.net/download/hosts.txt
# http://pgl.yoyo.org/adservers/serverlist.php?hostformat=dnsmasq&showintro=0&mimetype=plaintext
# http://someonewhocares.org/hosts/hosts
#
# manual download helper script: DownloadHostsFiles.sh


# Some input hosts files are a bit too restrictive. So the entries in
# this list won't be included in the output file
_url_filter = [
    "blogspot.com"
]

# output formats
_dnsmasq_format = 'address=/{0}/127.0.0.1'.format
_hosts_file_format = '127.0.0.1 {0}'.format
_unbound_format = 'local-zone: "{0}" redirect\nlocal-data: "{0} A 127.0.0.1"'.format


def relevant(line):
    """
    Check if a line even needs to be considered for parsing
    :param line: to inspect
    :return: True/False
    """
    return not line.startswith('#') and len(line) > 0 and not line.isspace()


def url_part(parts):
    """
    Depending on the element count return the url/domain part in of the list
    :param parts: list with the parts of a split line as elements
    :return: domain name or None
    """
    elements = len(parts)
    if elements > 1:
        return parts[1]
    elif elements > 0:
        return parts[0]
    return None


class HostsConverter:
    # info message per file
    _file_info = 'file: {0} has {1} lines, relevant: {2} split: {3} ' \
                 'unfiltered lines {4}'.format

    # message string to display at the end of extraction
    _extract_msg = 'overall line count {0}\nunique unfiltered ' \
                   'domains: {1}'.format

    def __init__(self, path, output_format, output_file, print_stats):
        self._working_dir = path
        self._domains = set()
        self._line_count = 0
        self._output_format = output_format
        self._print_stats = print_stats
        self._output_file = output_file

    def convert(self):
        """
        Convert/Merge all files in file_paths to one big host/dnsmasq file and
        output some statistics at the end
        """
        print('working dir: {0}'.format(self._working_dir))

        file_paths = glob(os.path.join(self._working_dir, '*.hosts'))
        for filename in file_paths:
            self._parse_file(filename)

        self._write_file()

        if self._print_stats:
            print(self._extract_msg(self._line_count, len(self._domains)))

    def _write_file(self):
        """
        Writes the collected DNS entries to an output file
        """
        file_path = os.path.join(self._working_dir, self._output_file)
        with open(file_path, 'w') as output_file:
            for domain in self._domains:
                output_file.write(self._output_format(domain) + '\n')
            output_file.close()

    def _parse_file(self, file_path):
        """
        Parse one file for domain names and output some file statistics
        :param file_path: path to the input file
        """
        line_count = 0
        relevant_lines = 0
        url_count = 0
        added_urls = 0

        with open(file_path, 'r') as input_file:
            for line in input_file:
                line_count += 1
                if relevant(line):
                    relevant_lines += 1
                    url = url_part(line.split())
                    if url:
                        url_count += 1
                        if url not in _url_filter:
                            added_urls += 1
                            self._domains.add(url)

            if self._print_stats:
                print(self._file_info(file_path, line_count, relevant_lines,
                                      url_count, added_urls))

            self._line_count += line_count
            input_file.close()


def usage():
    # TODO: print nice formatted usage information
    print('Usage: {0}'.format(os.path.basename(sys.argv[0])))
    print('Options:')
    print('-h, --help             shows this information')
    print('-o, --output filename  sets the name of the output file. default: ' \
          'hosts_out')
    print('-p, --path             working dir. default: cwd/pwd')
    print('-f, --format           output file format. possible: hosts, dnsmasq, unbound' \
          ' default: dnsmasq')
    print('-s, --stats            shows some file statistics')


def main(argv):
    path = os.getcwd()
    format_type = 'dnsmasq'
    output_format = _dnsmasq_format
    output_file = "hosts.out"
    print_stats = False

    _options_short = 'ho:p:f:s'
    _options_long = ['help', 'output=', 'path=', 'format=', 'stats']

    try:
        opts, args = getopt.getopt(argv, _options_short, _options_long)
    except getopt.GetoptError as err:
        print(err.message)
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-o', '--output'):
            output_file = arg
        elif opt in ('-p', '--path'):
            path = arg
        elif opt in ('-f', '--format'):
            format_type = arg
        elif opt in ('-s', '--stats'):
            print_stats = True

    formats = {'hosts': _hosts_file_format, 'dnsmasq': _dnsmasq_format, 'unbound': _unbound_format}
    if format_type in formats.keys():
        output_format = formats[format_type]
    else:
        usage()
        sys.exit(3)

    converter = HostsConverter(path, output_format, output_file, print_stats)
    converter.convert()


if __name__ == '__main__':
    main(sys.argv[1:])
