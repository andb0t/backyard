"""Communication with the analyses."""
import datetime
import json
import os
import pathlib

import requests
import threading

import env
import job_mng


def collect_results(analyses, form_data):
    """Summarize single analyis results into one json file."""
    _cid = form_data['id']
    result = {
        "id": _cid,
        "time": f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
        "URL": form_data['url'],
        "domain": form_data['domain'],
        "info": "Done",
        }

    for ana in analyses:
        _file_path = env.analysis(_cid, ana)['outfile']
        with open(_file_path) as result_file:
            result['analysis_' + ana] = json.load(result_file)

    _outfile_path = env.analysis(_cid)['resultfile']
    print('[ANALYSIS] storing results in ' + _outfile_path)
    with open(_outfile_path, 'w') as outfile:
        json.dump(result, outfile)


def perform_analysis(form_data):
    """Call the analyses."""
    _analyses = ['data_statistics', 'dummy', 'counting', 'spiderfoot']

    _cid = form_data['id']

    # make results directory
    pathlib.Path(env.analysis(_cid)['resultdir']).mkdir(parents=True, exist_ok=True)

    # check what data files are available
    if not os.path.isfile(env.scan(_cid)['resultfile']):
        print('[ANALYSIS] no data files available')
        return None

    # print analyses
    print("[ANALYSIS] running these analyses:")
    for ana in _analyses:
        print('[ANALYSIS] - ' + ana)

    def _req(ana):
        _target = job_mng.html_target(ana)
        _payload = form_data
        _payload['outfile'] = env.analysis(_cid, ana)['outfile']
        _payload['datadir'] = env.analysis(_cid)['datadir']
        _payload['analysis'] = ana.lower()
        return requests.post(_target, data=_payload)

    # call analyses
    threads = []
    for ana in _analyses:
        print('[ANALYSIS] process ' + ana + ': start!')
        thread = threading.Thread(target=_req, args=(ana,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("[ANALYSIS] create summary file ...")
    collect_results(_analyses, form_data)
    return 'DONE'
