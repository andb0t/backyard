import logging

from backyard.supervisor import config
from backyard.supervisor import pod
import backyard.api.proto.api_pb2 as api
from backyard.supervisor.mongo import db


async def start(a_id, scan, req):
    scanners = config.Config.get_instance().get_scanners()

    if not scan in scanners:
        logging.error('unknown scanner %s', scan)
        return api.ERROR

    scanner = scanners[scan]

    # Create a new scanner if not already there
    collection = db.scans
    res = await collection.count_documents({'$and': [{'domain': req.domain}, {'id': scan}]})
    if res == 0:
        logging.info('starting scan %s for %s', scan, req.domain)
        pod.run(scanner['image'], a_id, req.domain)

        # Save this scan to the db for reference
        document = {
            'id': scan,
            'domain': req.domain,
            'progress': 0.0,
            'status': api.PENDING
        }
        result = await collection.insert_one(document)
        if result is None:
            return api.ERROR
    else:
        logging.debug('scan %s for %s already exists - not starting another one', scan, req.domain)

    # If successful, create entry in mongodb
    return api.OK


async def update(scanner, domain, req):
    collection = db.scans

    if req.status == api.READY:
        # Remove ready scans from mongodb
        result = await collection.delete_many({'$and': [{'id': scanner}, {'domain': domain}]})
        if result is None:
            logging.error('unable to remove scanner entry')
            return

    else:
        # Update scanner information
        u = {
            'progress': req.completed,
            'status': req.status
        }

        result = await collection.update_one({'$and': [{'id': scanner}, {'domain': domain}]}, {'$set': u})
        if result is None:
            logging.error('failed to update scanner run')
