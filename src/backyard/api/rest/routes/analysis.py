import logging
import os

from aiohttp import web
from bson.json_util import dumps
from google.protobuf.json_format import MessageToJson
from nats.aio.errors import ErrTimeout

import backyard.api.proto.api_pb2 as api
from backyard.api import utils
from backyard.api.__main__ import nc
from backyard.supervisor.mongo import db


logger = logging.getLogger(__name__)


async def create(request):  # noqa: E501
    """Start a new analysis

     # noqa: E501

    :param request:
    :type request: dict | bytes

    :rtype: AnalyserResponse
    """
    # Send a request to the analyzer service
    ar = api.AnalyserRequest()
    ar.domain = request.get('domain')
    ar.analyzer = request.get('analyzer')

    try:
        response = await nc.request("analyzer.request", ar.SerializeToString(), 1.0)
        resp = api.AnalyserResponse()
        resp.ParseFromString(response.data)
        print("Received response: {message}".format(
            message=resp))
        return web.Response(text=MessageToJson(resp), content_type="application/json")
    except ErrTimeout:
        raise web.HTTPGatewayTimeout(reason='Request timed out')


async def delete(id):  # noqa: E501
    """Delete analysis

    This can only be done by the logged in user. # noqa: E501

    :param id: The ID of the analysis
    :type id: str

    :rtype: None
    """
    if not utils.is_uuid(id):
        raise web.HTTPBadRequest(reason='Invalid ID supplied')

    try:
        result = await db.analyzer.deleteOne({'id': id})
        if result.deleted_count == 1:
            return web.Response()
        else:
            raise web.HTTPNotFound(reason='Analysis not found')

    except Exception as e:
        logger.error('Error deleting analyzer entry: %s' % e)
        raise web.HTTPInternalServerError(reason='%s' % e)


async def read(id):  # noqa: E501
    """Get analysis by ID

     # noqa: E501

    :param id: The ID of the analysis
    :type id: str

    :rtype: Analysis
    """
    if not utils.is_uuid(id):
        raise web.HTTPBadRequest(reason='Invalid ID supplied')

    # Load analyzer entry from mongo
    collection = db.analyzer
    document = await collection.find_one({'id': id})
    if document is None:
        raise web.HTTPNotFound(reason='Analysis not found')

    return web.Response(text=dumps, content_type="application/json")


async def list_analyses():
    """Get a list of analyses"""
    result = []
    cursor = db.analyzer.find()
    for a in await cursor.to_list(length=100):
        result.append(a)

    return web.Response(text=dumps, content_type="application/json")


async def read_result(request_ctx, id):  # noqa: E501
    """Access result.json from filesystem

    :param path: file path
    :type path: string
    """
    collection = db.analyzer
    document = await collection.find_one({'id': id})
    if document is None:
        raise web.HTTPNotFound(reason='Analysis not found')

    p = "/tmp" + document["path"]
    if not os.path.exists(p):
        raise web.HTTPNotFound(reason='Analysis not found')

    with open(p, 'rb') as f:
        resp = web.StreamResponse(headers={
            'CONTENT-DISPOSITION': 'attachment; filename="%s"' % p
        })
        resp.content_type = 'application/json'
        data = f.read()
        resp.content_length = len(data)
        await resp.prepare(request_ctx)
        await resp.write(data)
        return resp
