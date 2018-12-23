import asyncio
import json
import os
import time
import random
from xml.etree import ElementTree

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrNoServers

import backyard.api.proto.api_pb2 as api


nc = NATS()


async def run(loop):
    analyzer_id = os.environ['ANALYZER']
    domain = os.environ['DOMAIN']
    scanner_id = 'THEHARVESTER'
    status_topic = 'scanner.%s.status' % scanner_id

    # Connect to nats
    try:
        print('connecting to nats server...')
        await nc.connect("localhost:4222", loop=loop)
    except ErrNoServers as e:
        print('failed to connect to nats', e)
        return
    except Exception as e:
        print('Error: %s' % e)

    # start the dummy process
    runtime = 60
    now = 0

    try:
        status = api.JobStatus()
        status.id = analyzer_id
        status.status = api.SCANNING
        status.completed = 0
        print('sending %s completed to nats topic: %s' % (status.completed, status_topic))
        await nc.publish(status_topic, status.SerializeToString())
        await nc.flush(0.500)

        # define output paths
        folder = '/data/' + domain
        file_base = folder + '/' + scanner_id
        html_file = file_base + '.html'
        xml_file = file_base + '.xml'
        json_file = file_base + '.json'
        print('Saving to file {} and {}'.format(html_file, xml_file))

        # define command
        data_source = "bing"
        _cmd = "cd {} && theharvester -d {} -b {} -f {}".format(folder, domain, data_source, html_file)

        # run it
        print("Executing: " + _cmd)
        os.system(_cmd)

        status.completed = 50
        print('sending %s completed to nats topic: %s' % (status.completed, status_topic))
        await nc.publish(status_topic, status.SerializeToString())
        await nc.flush(0.500)

        # parse the output
        search_strings = {'email': 'email',
                          'host_name': 'host',
                          'virtual_host_name': 'vhost',
                          'tld': 'tld',
                          'shodan': 'shodan'}
        result = {key: [] for key in search_strings}

        parsed_data = ElementTree.parse(xml_file)
        for key, value in search_strings.items():
            occurences = parsed_data.findall(value)
            for occurence in occurences:
                finding = occurence.text
                if finding:
                    result[key].append(finding)
                else:
                    ip_adr = occurence.find('ip').text
                    host_name = occurence.find('hostname').text
                    finding = {host_name: ip_adr}
                    result[key].append(finding)

        # save as json
        with open(json_file, 'w') as f:
            json.dump(result, f)

        status.completed = 100
        print('sending %s completed to nats topic: %s' % (status.completed, status_topic))
        await nc.publish(status_topic, status.SerializeToString())
        await nc.flush(0.500)

        # send the ScanCompleted message
        status.status = api.READY
        status.completed = 100
        status.path = json_file
        await nc.publish(status_topic, status.SerializeToString())
        await nc.flush(0.500)
        await nc.drain()
    except Exception as e:
        print('Error: %s' % e)


def main():
    print('starting...')
    loop = asyncio.get_event_loop()
    task = loop.create_task(run(loop))
    loop.run_until_complete(task)
    print('done')


if __name__ == "__main__":
    main()
