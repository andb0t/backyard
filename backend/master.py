import json
import os
import sys

import analysis
import worker


def backend_get(url):

    # Check if (valid, up to date) json is already there and return it
    filepath = 'data/result_{}.json'.format(url)
    if os.path.isfile(filepath):
        print("Returning analysis result of {} to FE ...".format(url))
        with open(filepath) as f:
            json_data = json.load(f)
        print('json data from within backend:')
        print(json_data)
        return json_data

    # Check if data for analysis is already there and perform analysis
    datapath = 'data/data_{}.json'.format(url)
    if os.path.isfile(datapath):
        analysis.perform_analysis(url)
        return backend_get(url)

    # Gather reconnessaince data
    worker.gather_data(url)
    return backend_get(url)


if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'www.script.backend.example.com'
    backend_get(url)
