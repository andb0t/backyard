import asyncio
import os
import time
import random
import json

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrNoServers

import backyard.api.proto.api_pb2 as api


nc = NATS()


async def run(loop):
    analyzer_id = os.environ['ANALYZER']
    domain = os.environ['DOMAIN']
    scanner_id = 'ARACHNI'
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

    try:
        status = api.JobStatus()
        status.id = analyzer_id
        status.status = api.SCANNING
        await nc.publish(status_topic, status.SerializeToString())
        await nc.flush(0.500)

        # prerequisites
        result_dir = '/result'
        result_file = 'result.json'
        result_path = '{}/{}'.format(result_dir, result_file)
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        folder = '/data/' + domain
        file_base = folder + '/' + scanner_id
        if not os.path.exists(file_base):
            os.makedirs(file_base)
        json_file = file_base + '.json'

        # run scan
        print('Running scan...')
        os.system('arachni --scope-include-subdomains --output-only-positives {} --report-save-path=result.afr'.format(domain))
        os.system('arachni_reporter result.afr --reporter=json:outfile={}'.format(result_path))

        with open(result_path, 'r+') as f:
            data = json.load(f)
            #TODO: further modifications

        print('Saving to file {}'.format(json_file))
        with open(json_file, 'w') as f:
            json.dump(data, f)

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
