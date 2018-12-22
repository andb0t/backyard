import asyncio
import os
import time
import random

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

        print('sending %s completed to nats topic: %s' % (0, status_topic))
        await nc.publish(status_topic, status.SerializeToString())
        await nc.flush(0.500)

        # save result and
        folder = '/data/%s' % domain
        file = '%s.html' % scanner_id
        full_file = os.path.join(folder, file)
        print('Saving to file %s' % full_file)
        # define command
        data_source = "bing"
        _cmd = "cd {} && theharvester -d {} -b {} -f {}".format(folder, domain, data_source, file)
        # run it
        print("Executing: " + _cmd)
        os.system(_cmd)

        print('sending %s completed to nats topic: %s' % (100, status_topic))
        await nc.publish(status_topic, status.SerializeToString())
        await nc.flush(0.500)

        # send the ScanCompleted message
        status.status = api.READY
        status.completed = 100
        status.path = full_file
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
