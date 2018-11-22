"""A webapp."""
from __future__ import print_function

import json
import os
import re
import time

import flask
import requests


app = flask.Flask(__name__)

@app.route('/', methods=['POST'])
def get_spiderfoot_result():
    """Call SpiderFoot."""
    # register modules
    modules = ['sfp_pwned', 'sfp_phishtank', 'sfp_pastebin', 'sfp_names', 'sfp_dnsresolve']
    def html_target(name="SCAN_SPIDERFOOT_SERVER"):
        # for now just copied from master
        # TODO: find way to use functions from other dir in docker container and use the html_target function there
        key_list = list(dict(os.environ).keys())
        regex_string = r'.*' + name.upper() + r'_PORT_\d{4}_TCP_PORT'
        port_key = list(filter(lambda x: re.match(regex_string, x), key_list))[0]
        _port = os.environ[port_key]
        regex_string = r'.*' + name.upper() + r'_PORT_{}_TCP_ADDR'.format(_port)
        addr_key = list(filter(lambda x: re.match(regex_string, x), key_list))[0]
        _addr = os.environ[addr_key]
        # _addr = os.environ["{}_PORT_{}_TCP_ADDR".format(name.upper(), _port)]
        return "http://{}:{}/".format(_addr, _port)

    def get_valid_url(url):
        """Format the url to be accepted by SpiderFoot server"""
        regex = re.compile(r"http://(.*)")
        finding = regex.search(url)
        if finding is not None:
            return finding.group(1)

        return url

    print("Calling the spiderfoot server to analyse {} using those modules:".format(flask.request.form['url']))
    for module in modules:
        print("- " + module)

    # run it
    sf_modules = ','.join(modules)
    print('Posting requests to ' + html_target() + ' ...')
    url = get_valid_url(flask.request.form['url'])
    payload = {'scanname': flask.request.form['id'],
               'scantarget': url,
               'usecase': 'all',
               'modulelist': sf_modules,
               'typelist': ''}
    response = requests.post(html_target() + "/startscan", payload)
    regex = re.compile(r"Internal ID:<\/td><td>(.*)<\/td>")
    finding = regex.search(response.text)
    scan_id = finding.group(1)
    print('Scan {} started!'.format(scan_id))

    # wait for all scans to finish
    status = None
    is_done = False
    while not is_done:
        response = requests.get(html_target() + "/scanstatus?id={}".format(scan_id))
        status = json.loads(response.text)[-1].strip()
        is_done = status not in ['STARTING', 'RUNNING']
        if not is_done:
            print('Scan {} still running ...'.format(scan_id))
            time.sleep(2)

    if status == 'FINISHED':
        print('Scan {} finished!'.format(scan_id))
    else:
        print('Scan {} finished with error!'.format(scan_id))
        print('Problem status flag: {}'.format(status))
        response = requests.get(html_target() + "/scanlog?id={}".format(scan_id))
        log = json.loads(response.text)
        _log_file = '/data/scan_results/{}/log_spiderfoot.txt'.format(flask.request.form['id'])
        print('Dumping log to ' + _log_file)
        with open(_log_file, 'w') as myfile:
            print(log, file=myfile)

    # download results
    response = requests.get(html_target() + "/scaneventresultexportmulti?ids={}".format(scan_id))
    _output_file = '/data/scan_results/{}/data_spiderfoot.csv'.format(flask.request.form['id'])
    print('Saving scan results in ' + _output_file)
    with open(_output_file, 'w') as myfile:
        print(response.text.encode('utf-8'), file=myfile)

    print('Done!')
    return 'Finished!'


if __name__ == '__main__':
    _port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=_port)
