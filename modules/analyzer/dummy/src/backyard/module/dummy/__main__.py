import asyncio
import json
import os
import sys

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrNoServers

import backyard.api.proto.api_pb2 as api


nc = NATS()


async def run(loop, json_file):
    analyzer_id = os.environ['ANALYZER']
    domain = os.environ['DOMAIN']
    module_id = 'DUMMY'
    folder = '/data/%s' % domain
    status_topic = 'analyzer.%s.status' % module_id

    # Connect to nats
    try:
        print('connecting to nats server...')
        await nc.connect("localhost:4222", loop=loop)
    except ErrNoServers as e:
        print('failed to connect to nats', e)
        return
    except Exception as e:
        print('Error: %s' % e)

    status = api.JobStatus()
    status.id = analyzer_id
    status.status = api.ANALYZING
    await nc.publish(status_topic, status.SerializeToString())
    await nc.flush(0.500)

    file = os.path.join(folder, 'result-%s.json' % analyzer_id)

    with open(json_file, 'w') as f:
        dummy_data = json.loads(f)

    with open(file, 'w') as f:
        f.write(json.dumps(dummy_data))

    status.status = api.READY
    status.completed = 100
    status.path = file
    await nc.publish(status_topic, status.SerializeToString())
    await nc.flush(0.500)
    await nc.drain()


def main():
    print('starting...')
    loop = asyncio.get_event_loop()
    task = loop.create_task(run(loop, sys.argv[1]))
    loop.run_until_complete(task)
    print('done')


if __name__ == "__main__":
    main()
