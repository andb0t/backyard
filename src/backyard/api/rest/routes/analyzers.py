import logging

from aiohttp import web
from google.protobuf.json_format import MessageToJson
from nats.aio.errors import ErrTimeout

import backyard.api.proto.api_pb2 as api
from backyard.api.__main__ import nc


logger = logging.getLogger(__name__)


async def list():  # noqa: E501
    """Get a list of available analyzers

    :rtype: ListAnalyzerResponse
    """
    # Send a request to the analyzer service
    ar = api.ListAnalyzerRequest()

    try:
        response = await nc.request("analyzer.list", ar.SerializeToString(), 1.0)
        resp = api.ListAnalyzerResponse()
        resp.ParseFromString(response.data)
        logger.debug("Received response: {message}".format(message=resp))
        return web.Response(text=MessageToJson(resp), content_type="application/json")
    except ErrTimeout:
        raise web.HTTPGatewayTimeout(reason='Request timed out')
