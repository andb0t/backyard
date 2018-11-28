import logging
import os
import traceback
import uuid

import backyard.supervisor.config as config
import backyard.supervisor.pod as pod
import backyard.api.proto.api_pb2 as api
import backyard.supervisor.scanner as scanner
from backyard.supervisor.mongo import db


async def start(req):
    analyzers = config.Config.get_instance().get_analyzers()

    analyzer = None
    for _analyzer in analyzers:
        if req.analyzer == _analyzer['id']:
            analyzer = _analyzer
            break

    if not analyzer:
        logging.error('unknown analyzer %s', req.analyzer)
        return "", api.ERROR

    a_id = str(uuid.uuid4())

    p = os.path.join("/tmp", "data", req.domain)
    if not os.path.exists(p):
        os.makedirs(p)
        os.chmod(p, 0o777)

    # Save this analyzer run to the db for reference
    collection = db.analyzer
    document = {
        'id': a_id,
        'domain': req.domain,
        'image': analyzer['image'],
        'progress': 0.0,
        'completed': False,
        'status': api.PENDING,
        'scanners': analyzer['scanners'],
        'results': {},
        'path': ''
    }
    result = await collection.insert_one(document)
    if result is None:
        logging.error('failed to insert analyzer run')
        return "", api.ERROR

    logging.info('starting scans for analysis:')
    for scan in analyzer['scanners']:
        res = await scanner.start(a_id, scan, req)
        if res != api.OK:
            logging.error('failed to start scanner %s' % scan)
            return "", api.ERROR

    # If successful, create entry in mongodb
    return a_id, api.OK


async def scan_status_handler(msg):
    try:
        logging.info('message received')
        req = api.JobStatus()
        req.ParseFromString(msg.data)

        a_id = req.id
        parts = msg.subject.split('.')
        _scanner = parts[1]

        # Load analyzer entry from mongo
        collection = db.analyzer
        document = await collection.find_one({'id': a_id})

        # Valid scanner?
        if document is None:
            logging.warning('unknown analysis - skipping')
            return
        if not _scanner in document['scanners']:
            logging.warning('invalid scanner for current analyzer')
            return

        # Scanner ready?
        if req.status == api.READY:
            update = {}

            # Remove this scanner from the current analysis
            scanners = document['scanners']
            scanners.remove(_scanner)
            update['scanners'] = scanners
            update['results'] = document['results']
            update['results'][_scanner] = req.path

            # We're the last one so - tadaa, we're ready
            if len(scanners) == 0:
                update['status'] = api.ANALYZING
                logging.info("all scanners for %s are ready" % a_id)
                document['results'] = update['results']
                start_analyzer(document)
            else:
                logging.info('scanner %s for %s: %d%% completed' % (_scanner, a_id, req.completed))

            result = await collection.update_one({'id': a_id}, {'$set': update})
            if result is None:
                logging.error('failed to update analyzer run')
                return

            await scanner.update(_scanner, document['domain'], req)

        # ... not ready - update status
        else:
            update = {}
            if document['status'] == api.PENDING:
                update['status'] = api.SCANNING

                result = await collection.update_one({'id': a_id}, {'$set': update})
                if result is None:
                    logging.error('failed to update analyzer run')
                    return

            # TODO: handle errors (status ERROR, etc.)

            logging.info('scanner %s for %s: %d%% completed' % (_scanner, a_id, req.completed))

    except Exception as e:
        logging.error(e)
        traceback.print_exc()


async def analyzer_status_handler(msg):
    try:
        logging.info('message received')
        req = api.JobStatus()
        req.ParseFromString(msg.data)

        a_id = req.id
        parts = msg.subject.split('.')
        _analyzer = parts[1]

        # Load analyzer entry from mongo
        collection = db.analyzer
        document = await collection.find_one({'id': a_id})

        # Valid?
        if document is None:
            logging.warning('unknown analysis - skipping')
            return

        # Ready?
        if req.status == api.READY:
            update = {}
            update['status'] = api.READY
            update['path'] = req.path

            result = await collection.update_one({'id': a_id}, {'$set': update})
            if result is None:
                logging.error('failed to update analyzer run')
                return

            logging.info('analyzer %s is ready: %s' % (_analyzer, req.path))

        # ... not ready - update status
        else:
            update = {}
            if document['status'] == api.PENDING:
                update['status'] = api.ANALYZING

                result = await collection.update_one({'id': a_id}, {'$set': update})
                if result is None:
                    logging.error('failed to update analyzer run')
                    return

            # TODO: handle errors (status ERROR, etc.)

            logging.info('analyzer %s for %s: %d%% completed' % (_analyzer, a_id, req.completed))

    except Exception as e:
        logging.error(e)
        traceback.print_exc()


def start_analyzer(dsc):
    logging.info('starting analyzer image %s for domain %s' % (dsc['image'], dsc['domain']))
    pod.run(dsc['image'], dsc['id'], dsc['domain'], dsc['results'])
