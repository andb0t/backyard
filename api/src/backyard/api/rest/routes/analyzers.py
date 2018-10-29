import logging

import backyard.api.proto.api_pb2 as api
from aiohttp import web
from backyard.api.__main__ import nc
from google.protobuf.json_format import MessageToJson
from nats.aio.errors import ErrTimeout

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
        return web.json_response(MessageToJson(resp))
    except ErrTimeout:
        raise web.HTTPGatewayTimeout(reason='Request timed out')
