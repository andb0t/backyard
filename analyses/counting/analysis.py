import json
import os
import sys
from xml.etree import ElementTree


def run(data_dir):

    print('Opening datafile in ' + data_dir)

    file_name = 'results.xml'
    full_file = os.path.abspath(os.path.join(data_dir, file_name))


    dom = ElementTree.parse(full_file)

    f = dom.findall('email')


    for e in f:
        email_adr = e.text
        print(email_adr)

    h = dom.findall('host')

    result = {}

    for n in h:
        host_name = n.find('ip').text
        ip_adr = n.find('hostname').text
        # description = n.find('description').text
        # print(' * {} {} {} '.format(name, price, description))
        result[host_name] = ip_adr
    # print(result)
    print(json.dumps(result, indent = 4))
    return result


if __name__ == '__main__':
    run(sys.argv[1])
