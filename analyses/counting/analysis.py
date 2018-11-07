import json
import os
import sys
from xml.etree import ElementTree


def run(data_dir):

    print('Opening datafile in ' + data_dir)

    file_name = 'myresults.xml'
    full_file = os.path.abspath(os.path.join(data_dir, file_name))

    parsed_data = ElementTree.parse(full_file)

    result_details = {'email' : {}, 'Host_name': {}, 'Virtual_Host_name': {}, 'TLD':{}, 'Shodan':{}}
    result = {'n_emails':{}, 'n_hostnames':{},'n_virtual_hostnames':{}}

    # Emails
    occurances = parsed_data.findall('email')

    for occurance in occurances:
        email_adr = occurance.text
        result_details['email'][email_adr] = email_adr

    result['n_emails'] = len(result['email'])


    # Hostnames - IP addresses
    h = parsed_data.findall('host')

    for n in h:
        host_name = n.find('ip').text
        ip_adr = n.find('hostname').text
        result_details['Host_name'][host_name] = ip_adr

    result['n_hostnames'] = len(result['Host_name'])


    # VirtualHosts - IP addresses
    vh = parsed_data.findall('vhost')

    for m in vh:
        vhost_name = m.find('hostname').text
        ip_adr_v = m.find('ip').text
        result_details['Virtual_Host_name'][vhost_name] = ip_adr_v

    result['n_virtual_hostnames'] = len(result['Virtual_Host_name'])

    # TLD
    t = parsed_data.findall('tld')

    # Shodan
    s = parsed_data.findall('shodan')

    # print data in JSON format
    print(json.dumps(result, indent = 4))
    print(json.dumps(result_details, indent = 4))

    return result


if __name__ == '__main__':
    run(sys.argv[1])
