#!/usr/bin/env python3
import asyncio

from backyard.api.rest.server import RestServer
import logging
from logging.config import dictConfig
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

logging.basicConfig(level=logging.DEBUG)

nc = NATS()

dictConfig({
    'version': 1,
    'keys': ['root', 'connexion'],
    'handlers': {
        'console': {
            'class': 'colorlog.StreamHandler',
            'formatter': 'console'
        }
    },
    'formatters': {
      'console': {
          'format': '%(log_color)s%(asctime)s %(levelname)s: [%(threadName)s] %(name)s - %(message)s',
          'class': 'colorlog.ColoredFormatter'
      }
    },
    'root': {
        'handlers': ['console'],
        'level': logging.DEBUG
    },
    'connexion': {
        'handlers': ['console'],
        'level': logging.DEBUG,
        'qualname': 'connexion.app'
    }
})

logger = logging.getLogger(__name__)


async def run(loop):

    # Connect to nats
    try:
        logger.debug('connecting to nats server...')
        await nc.connect("localhost:4222", loop=loop)
    except ErrNoServers as e:
        logger.error('failed to connect to nats', e)
        return


def main():
    logger.debug('starting...')
    loop = asyncio.get_event_loop()
    task = loop.create_task(run(loop))
    loop.run_until_complete(task)

    server = RestServer()
    server.start(port=8080)


if __name__ == "__main__":
    main()
