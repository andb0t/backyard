import asyncio
import os
import time
import random
import subprocess
import shlex

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrNoServers

import backyard.api.proto.api_pb2 as api


nc = NATS()


def execute(strcmd):
    cmd = shlex.split(strcmd)
    popen = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


async def run(loop):
    analyzer_id = os.environ['ANALYZER']
    domain = os.environ['DOMAIN']
    scanner_id = 'WAPITI'
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

        analyzers = ['sql', 'exec', 'permanentxss',
                     'xss', 'shellshock', 'blindsql']

        # define command
        _result_file = "/data/%s/data_wapiti.xml" % domain
        _ssl_addon = '--verify-ssl 1' if domain.startswith('https') else ''
        _cmd = "wapiti -u {}/  -m \"{}\" -d 10 --max-links-per-page 15"\
            " --max-files-per-dir 30 -f xml --max-scan-time 15 {} -o {}".\
            format(domain, ",".join(analyzers), _ssl_addon, _result_file)

        # run it
        module_counter = -1  # used to track progress; offset of -1 because: when the first message appears, no module scan has finished yet
        print("Executing: " + _cmd)
        for line in execute(_cmd):
            print("Stdout: %s" % line)
            if line.startswith('[*] Launching module '):
                module_counter += 1
                status.completed = min(100, round(
                    module_counter / len(analyzers) * 100))
                print('sending %s completed to nats topic: %s' %
                      (status.completed, status_topic))
                await nc.publish(status_topic, status.SerializeToString())
                await nc.flush(0.500)

        # send the ScanCompleted message
        status.status = api.READY
        status.completed = 100
        status.path = _result_file
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
