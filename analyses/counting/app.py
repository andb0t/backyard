import datetime
import glob
import json
import os
import time

import flask

import analysis


app = flask.Flask(__name__)


@app.route('/', methods=['POST'])
def do_analysis():
    # check what data files are available
    data_dir = flask.request.form['datadir']
    data_files = glob.glob(data_dir + "*")
    print("found those datafiles:")
    for file in data_files:
        print('- ' + file)

    print('perform analysis {} ...'.format(flask.request.form['analysis']))

    result = {
        "id": flask.request.form['id'],
        "time_start_wall": f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
        "URL": flask.request.form['url'],
        "domain": flask.request.form['domain'],
        "analysis": flask.request.form['analysis'],
        "info": "Done",
        }

    # run the analysis
    wall_start = time.time()
    cpu_start = time.process_time()
    result['result'] = analysis.run(data_dir)
    wall_end = time.time()
    cpu_end = time.process_time()
    result['time_duration_wall'] = wall_end - wall_start
    result['time_duration_cpu'] = cpu_end - cpu_start
    result['time_end_wall'] = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"

    # save results
    outfilepath = flask.request.form['outfile']
    print('Storing results in ' + outfilepath)
    with open(outfilepath, 'w') as outfile:
        json.dump(result, outfile)

    # return something
    return 'Finished analysis: ' + flask.request.form['id']


if __name__ == '__main__':
    _port = int(os.environ.get('PORT', 5009))
    app.run(host='0.0.0.0', port=_port)
