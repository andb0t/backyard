import asyncio
import os
import time
import datetime
import random

from gvm.connections import UnixSocketConnection
from gvm.protocols.latest import Gmp
from gvm.transforms import EtreeTransform
from gvm.xml import pretty_print

from lxml import etree

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrNoServers

import backyard.api.proto.api_pb2 as api

def connect():
    # connect to the Greebon Management Protocol (GMP)
    try:
        connection = UnixSocketConnection(path='/var/run/redis-openvas/redis-server.sock')
        transform = EtreeTransform()
        print('Connecting GMP Server...')
        # Greenbone Management Protocol (deletegator)
        gmp = Gmp(connection=connection, transform=transform)
        return gmp
    except Exception as e:
        print('Error on connecting GMP Server: %s' % e)

def get_target_id(gmp, name):
    result = gmp.get_targets()
    selector = "target/@id[../name/text() = '%s']" % name
    return result.xpath(selector)

def create_target(gmp, name, hosts):
    print('Creating a target...')
    result = gmp.create_target(name=name, hosts=['127.0.0.1'])
    #result example
    #<create_target_response status="201" status_text="OK, resource created" id="d2173eea-1a7d-486c-9c2a-36b60fafcdc0"/>

    status_list = result.xpath('@status')
    if status_list and int(status_list[0]) == 201:
        target_id = result.xpath('@id')[0]
        print('Target created:', target_id)
        return target_id
    elif status_list and int(status_list[0]) == 201:
        #target already exists. example:
        #<create_target_response status="400" status_text="Target exists already"/>
        return get_target_id(gmp, name)
    else:
        print('Error! Creating target failed.')
        pretty_print(result)

def get_config_id(gmp, config_name):
    print('Searching for matched config...')
   
    for config in gmp.get_configs().xpath('config'):
        name = config.xpath('name/text()')
        if name and name[0] == config_name:
            config_id = config.xpath('@id')[0]
            print(config_name, ':', config_id)
            return config_id  
    
    print('Error! No matched config found.')   

def get_scanner_id(gmp, scanner_name):
    print('Searching for matched scanner...')
   
    for scanner in gmp.get_scanners().xpath('scanner'):
        name = scanner.xpath('name/text()')
        if name and name[0] == scanner_name:
            scanner_id = scanner.xpath('@id')[0]
            print(scanner_name, ':', scanner_id)
            return scanner_id  
    
    print('Error! No matched scanner found.') 

def create_task(gmp, task_name, config_id, target_id, scanner_id):
    print('Creating a task...')

    result = gmp.create_task(name=task_name, config_id=config_id, target_id=target_id, scanner_id=scanner_id)
    #result example
    #<create_task_response status="201" status_text="OK, resource created" id="9a191590-bdf1-4493-aa6a-fb8f60316cc9"/>
    status_list = result.xpath('@status')
    if status_list and int(status_list[0]) == 201:
        task_id = result.xpath('@id')[0]
        print('Task created:', task_id)
        return task_id
    else:
        print('Error! Creating task failed.')

#TODO: customized scan policies could be created in docker and called here with names

def run_task(gmp, task_id):
    print('Starting the task:', task_id)
    
    result = gmp.start_task(task_id)
    #result example
    #<start_task_response status="202" status_text="OK, request submitted">
    #    <report_id>ec24c67f-5640-4fed-ae2b-44c8abac2fff</report_id>
    #</start_task_response>
    status_list = result.xpath('@status')
    if status_list and int(status_list[0]) == 202:
        report_id = result.xpath('report_id/text()')[0]
        print('Report created:', report_id)
        return report_id
    else:
        print('Error! Running task failed.')

def is_task_done(gmp, task_id):
    result = gmp.get_task(task_id)
    progress_list = result.xpath('task/progress/text()')
    if progress_list:
        if int(progress_list[0]) == -1:
            return True
    else:
        print('Error! No progress tag found.')

def save_xml(root, file_name):
    tree = etree.ElementTree(root)
    with open(file_name, 'wb') as f:
        f.write(etree.tostring(tree))

def execute(domain, scanner_id):
    # define output paths
    folder = '/data/' + domain
    file_base = folder + '/' + scanner_id
    xml_file = file_base + '.xml'
    json_file = file_base + '.json'
    print('Saving to file {}'.format(xml_file))

    gmp = connect()
    if gmp is None:
        print('No Scan is executed since no connection...')
        return
    
    # using the with statement to automatically connect and disconnect to gvmd
    with gmp:
        # Login
        # default user and password
        login_result = gmp.authenticate('admin', 'admin')
        print('Login status:', login_result)

        print("Executing: ...")
        # Retrieve current GMP version
        version = gmp.get_version()
        # Prints the XML in beautiful form
        pretty_print(version)

        target_name = 'OpenVAS Target: ' + domain
        target_id = create_target(gmp, name=target_name, hosts=[domain])

        config_id = get_config_id(gmp, 'Full and fast')
        scanner_id = get_scanner_id(gmp, 'OpenVAS Default')
        
        taks_name = domain + ' Task: ' + datetime.datetime.now()
        task_id = create_task(gmp, taks_name , config_id, target_id, scanner_id)
        run_task(task_id)

        #check the status until the task is done
        while not is_task_done(task_id):
            time.sleep(5)

        print('Task is finished.')

        scan_result = gmp.get_results(task_id=task_id)

        save_xml(scan_result, xml_file)

    return json_file, xml_file


def parse(xml_file):
    search_strings = {'email': 'email',
                      'host_name': 'host',
                      'virtual_host_name': 'vhost',
                      'tld': 'tld',
                      'shodan': 'shodan'}
    result = {key: [] for key in search_strings}

    parsed_data = ElementTree.parse(xml_file)
    for key, value in search_strings.items():
        occurences = parsed_data.findall(value)
        for occurence in occurences:
            finding = occurence.text
            if finding:
                result[key].append(finding)
            else:
                ip_adr = occurence.find('ip').text
                host_name = occurence.find('hostname').text
                finding = {host_name: ip_adr}
                result[key].append(finding)
    return result


def save(json_file, result):
    with open(json_file, 'w') as f:
        json.dump(result, f)


nc = NATS()


async def run(loop):
    analyzer_id = os.environ['ANALYZER']
    domain = os.environ['DOMAIN']
    scanner_id = 'OPENVAS'
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
        status.completed = 0
        print('sending %s completed to nats topic: %s' % (status.completed, status_topic))
        await nc.publish(status_topic, status.SerializeToString())
        await nc.flush(0.500)

        json_file, xml_file = execute(domain, scanner_id)

        status.completed = 50
        print('sending %s completed to nats topic: %s' % (status.completed, status_topic))
        await nc.publish(status_topic, status.SerializeToString())
        await nc.flush(0.500)

        # parse the output
        #result = parse(xml_file)

        status.completed = 75
        print('sending %s completed to nats topic: %s' % (status.completed, status_topic))
        await nc.publish(status_topic, status.SerializeToString())
        await nc.flush(0.500)

        # save as json
        save(json_file, result)

        status.completed = 100
        print('sending %s completed to nats topic: %s' % (status.completed, status_topic))
        await nc.publish(status_topic, status.SerializeToString())
        await nc.flush(0.500)

        # send the ScanCompleted message
        status.status = api.READY
        status.completed = 100
        status.path = json_file
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
