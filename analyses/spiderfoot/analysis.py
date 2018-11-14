"""The analysis result for SpiderFoot."""
import json
import sys

import pandas as pd
import spacy


nlpEN = spacy.load('en')
nlpDE = spacy.load('de')


def getModuleDummy(name):
    module = {}
    module['Module'] = name
    return module


def isGermanName(name):
    # name-like entries, e.g. "Kostenlose Service-Hotline" should return false
    humanName = False

    doc = nlpDE(name)
    endIndex = 0
    for ent in doc.ents:
        # print(ent.text, ent.start_char, ent.end_char, ent.label_)
        humanName = True
        endIndex = ent.end_char
        if ent.label_ != "PER":
            humanName = False
            break

    if humanName and endIndex < len(name):
        # including unprocessed part
        humanName = False

    return humanName

#
# def isEnglishName(name):
#     #name-like entries, e.g. "Kostenlose Service-Hotline" should return false
#     humanName = False
#
#     doc = nlpEN(name)
#     endIndex = 0
#     for ent in doc.ents:
#         #print(ent.text, ent.start_char, ent.end_char, ent.label_)
#         humanName = True
#         if ent.label_ != "PERSON":
#             humanName = False
#             break
#
#     if humanName and endIndex < len(name):
#         #including unprocessed part
#         humanName = False
#
#     return humanName


def filterNames(name_data):
    removal_list = []
    for name, count in name_data.items():
        # name-like entries, e.g. "Kostenlose Service-Hotline" could be removed here
        if not isGermanName(name):
            removal_list.append(name)

    print("Count of names:", len(name_data))
    print("After filtering German Words:", len(name_data) - len(removal_list))

    for name in removal_list:
        name_data = name_data.drop(labels=name)

    return name_data


def getCountsData(df, module_name, data_type):
    series = df.loc[(df['Module'] == module_name) & (df['Type'] == data_type)]['Data'].value_counts()
    return series


def getMapData(df, module_name, data_type, reverse=False):
    data = df.loc[(df['Module'] == module_name) & (df['Type'] == data_type)]

    series = None
    if not reverse:
        series = pd.Series(data['Data'].tolist(), index=data['Source'])
    else:
        series = pd.Series(data['Source'].tolist(), index=data['Data'])

    return series


# the major method defines which data to abstract and how to abstract them
def getData(df, module_name, data_type):
    data = None

    # sfp_names
    if module_name == 'sfp_names':
        # only HUMAN_NAME is handled while no other type exists in current data file
        if data_type == 'HUMAN_NAME':
            data = getCountsData(df, module_name, data_type)
            # name-like entries, e.g. "Kostenlose Service-Hotline" could be removed here
            data = filterNames(data)

    # sfp_dnsresolve
    if module_name == 'sfp_dnsresolve':
        if data_type == 'IP_ADDRESS':
            data = getMapData(df, module_name, data_type)

        if data_type == 'AFFILIATE_INTERNET_NAME':
            # TODO: value from this type looks like a IP-Host mapping but why it is affilicated?
            data = getMapData(df, module_name, data_type, True)

    if data is not None:
        # dict is automatically serializable
        data = data.to_dict()

    return data


def getTypes(df, module_name):
    return df.loc[df['Module'] == module_name]['Type'].unique()


def getModule(df, module_name):
    # get module data if defined
    result = {}
    for data_type in getTypes(df, module_name):
        data = getData(df, module_name, data_type)
        if data is not None:
            result[data_type] = data

    if len(result) == 0:
        # no data exists or defined
        return None

    module = getModuleDummy(module_name)
    module['Result'] = result

    return module


def run(data_dir):
    """Call the analysis."""
    print('Opening datafile in ' + data_dir)

    with open(data_dir + '/paths.json') as f:
        json_data = json.load(f)

    csv_file = data_dir + '/' + json_data['data']['file']
    df = pd.read_csv(csv_file, parse_dates=['Last Seen'], engine='python')

    # get data by SpiderFoot modules
    resultName = getModule(df, "sfp_names")
    resultDNS = getModule(df, "sfp_dnsresolve")

    result = json.dumps([resultName, resultDNS], indent=4)

    print(json.dumps(result, indent=4))

    return result


if __name__ == '__main__':
    run(sys.argv[1])
