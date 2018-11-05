import asyncio
import os
import time
import random
import backyard.api.proto.api_pb2 as api
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrNoServers

nc = NATS()


async def run(loop):
    analyzer_id = os.environ['ANALYZER']
    domain = os.environ['DOMAIN']
    scanner_id = 'EXAMPLE'

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
        while status.completed < 100:
            wait_for = random.randint(1, 5)
            now += wait_for
            time.sleep(wait_for)
            status.completed = min(100, round(100/runtime * now))
            print('sending %s completed to nats topic: scanner.%s.status' % (status.completed, scanner_id))
            await nc.publish('scanner.%s.status' % scanner_id, status.SerializeToString())
            await nc.flush(0.500)

        status.status = api.READY
        status.completed = 100
        status.status = api.READY
        await nc.publish('scanner.%s.status' % scanner_id, status.SerializeToString())
        await nc.flush(0.500)

        # save result and send the ScanCompleted message
        folder = '/data/%s' % domain
        if not os.path.exists(folder):
            os.makedirs(folder)
        file = os.path.join(folder, '%s.json' % scanner_id)
        with open(file) as f:
            f.write('{"result": "this scanner does nothing"}')
        status = api.ScanCompleted()
        status.id = analyzer_id
        status.path = file
        await nc.publish('scanner.%s.status' % scanner_id, status.SerializeToString())
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
