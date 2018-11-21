import json

import aiohttp
from aiohttp import web, WSMsgType
import logging
from backyard.api.__main__ import nc
from google.protobuf.json_format import MessageToJson

logger = logging.getLogger(__name__)


async def subscribe(request_ctx):
    """Websocket endpoint to subscribe to for status updates

    :rtype: JobStatus
    """
    ws = web.WebSocketResponse()
    await ws.prepare(request_ctx)

    async def status_message_handler(msg):
        subject = msg.subject
        reply = msg.reply

        protoMsg = api.JobStatus()
        protoMsg.ParseFromString(msg.data)
        data = MessageToJson(protoMsg)

        if isinstance(data, str):
            await ws.send_str(data, compress=None)
        else:
            await ws.send_json(data)

        logger.debug("Received a status message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))

    await nc.subscribe("analyzer.status", cb=status_message_handler)

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
        elif msg.type == WSMsgType.ERROR:
            logger.error('ws connection closed with exception %s' % ws.exception())
            raise web.HTTPServerError(reason='ws connection closed with exception %s' % ws.exception())

    logger.debug('websocket connection closed')
    return ws
