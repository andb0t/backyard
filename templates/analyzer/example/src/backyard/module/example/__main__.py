import asyncio
import json
import os

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrNoServers

import backyard.api.proto.api_pb2 as api


nc = NATS()


async def run(loop):
    analyzer_id = os.environ['ANALYZER']
    domain = os.environ['DOMAIN']
    scans = json.loads(os.environ['SCANS'])
    id = 'EXAMPLE'
    folder = '/data/%s' % domain
    status_topic = 'analyzer.%s.status' % id

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

    aggregated_data = {}
    for scanner_id, path in scans.items():
        with open(path) as f:
            aggregated_data[scanner_id] = f.read()
    aggregated_data['analysis_info'] = 'This analysis is an example ' \
        'and only shows the output of the dependent scanners!'

    file = os.path.join(folder, 'result-%s.json' % analyzer_id)
    with open(file, 'w') as f:
        f.write(json.dumps(aggregated_data))

    status.status = api.READY
    status.completed = 100
    status.path = file
    await nc.publish(status_topic, status.SerializeToString())
    await nc.flush(0.500)
    await nc.drain()


def main():
    print('starting...')
    loop = asyncio.get_event_loop()
    task = loop.create_task(run(loop))
    loop.run_until_complete(task)
    print('done')


if __name__ == "__main__":
    main()
