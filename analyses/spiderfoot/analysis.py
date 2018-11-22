"""The analysis result for SpiderFoot."""
import json
import os
import sys

import pandas as pd
import spacy


NLP_EN = spacy.load('en')
NLP_DE = spacy.load('de')


def get_module_dummy(name):
    """Return one module object contains nothing."""
    module = {}
    module['Module'] = name
    return module


def is_german_name(name):
    """Try to filter german words which are not human names."""
    # name-like entries, e.g. "Kostenlose Service-Hotline" should return false
    is_human_name = False

    doc = NLP_DE(name)
    end_index = 0
    for ent in doc.ents:
        # print(ent.text, ent.start_char, ent.end_char, ent.label_)
        is_human_name = True
        end_index = ent.end_char
        if ent.label_ != "PER":
            is_human_name = False
            break

    if is_human_name and end_index < len(name):
        # including unprocessed part
        is_human_name = False

    return is_human_name

#
# def isEnglishName(name):
#     #name-like entries, e.g. "Kostenlose Service-Hotline" should return false
#     humanName = False
#
#     doc = NLP_EN(name)
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


def filter_names(name_data):
    """Try to filter words which are not human names."""
    removal_list = []
    for name in name_data.items():
        # name-like entries, e.g. "Kostenlose Service-Hotline" could be removed here
        if not is_german_name(name):
            removal_list.append(name)

    print("Count of names:", len(name_data))
    print("After filtering German Words:", len(name_data) - len(removal_list))

    for name in removal_list:
        name_data = name_data.drop(labels=name)

    return name_data


def get_counts_data(data_frame, module_name, data_type):
    """Get the data column with their counts as a panda series."""
    typed_data = data_frame.loc[(data_frame['Module'] == module_name) &
                                (data_frame['Type'] == data_type)]
    series = typed_data['Data'].value_counts()
    return series


def get_mapped_data(data_frame, module_name, data_type, reverse=False):
    """Get the mapping data from the Source column and the Data column as a panda series."""
    data = data_frame.loc[(data_frame['Module'] == module_name) & (data_frame['Type'] == data_type)]

    series = None
    if reverse:
        series = pd.Series(data['Source'].tolist(), index=data['Data'])
    else:
        series = pd.Series(data['Data'].tolist(), index=data['Source'])

    return series


# the major method defines which data to abstract and how to abstract them
def get_data(data_frame, module_name, data_type):
    """Get the data from a specified module."""
    data = None

    # sfp_names
    if module_name == 'sfp_names':
        # only HUMAN_NAME is handled while no other type exists in current data file
        if data_type == 'HUMAN_NAME':
            data = get_counts_data(data_frame, module_name, data_type)
            # name-like entries, e.g. "Kostenlose Service-Hotline" could be removed here
            data = filter_names(data)

    # sfp_dnsresolve
    if module_name == 'sfp_dnsresolve':
        if data_type == 'IP_ADDRESS':
            data = get_mapped_data(data_frame, module_name, data_type, True)

        if data_type == 'AFFILIATE_INTERNET_NAME':
            # Notice: value from this type looks like a IP-Host mapping but why it is affilicated?
            data = get_mapped_data(data_frame, module_name, data_type)

    # sfp_pastebin
    if (module_name == 'sfp_pastebin'):
        if (data_type == 'LEAKSITE_CONTENT'):
            # site content found on pastebins (pure text storage on internet)
            data = get_mapped_data(data_frame, module_name, data_type)

        if(data_type == 'LEAKSITE_URL'):
            # site url found on pastebins (including query parameters etc.)
            data = get_mapped_data(data_frame, module_name, data_type, True)

    if data is not None:
        # dict is automatically serializable
        data = data.to_dict()

    return data


def get_types(data_frame, module_name):
    """Get data types belong to one module."""
    return data_frame.loc[data_frame['Module'] == module_name]['Type'].unique()


def get_module(data_frame, module_name):
    """Get module data if defined."""
    result = {}
    for data_type in get_types(data_frame, module_name):
        data = get_data(data_frame, module_name, data_type)
        if data is not None:
            result[data_type] = data

    if not result:
        # no data exists or defined
        return None

    module = get_module_dummy(module_name)
    module['Result'] = result

    return module


def run(data_dir):
    """Call the analysis."""
    print('Opening datafile in ' + data_dir)

    result = {}

    file_name = 'data_spiderfoot.csv'
    csv_file = os.path.abspath(os.path.join(data_dir, file_name))
    try:
        data_frame = pd.read_csv(csv_file, engine='python')
    except pd.errors.EmptyDataError:
        print('No data in ' + csv_file + ' ! Abort.')
        return {}

    # get data by SpiderFoot modules
    modules = ["sfp_names", "sfp_dnsresolve", "sfp_pastebin"]
    for module_name in modules:
        data = get_module(data_frame, module_name)
        if (data is not None):
            result[module_name] = data

    print(json.dumps(result, indent=4))

    return result


if __name__ == '__main__':
    run(sys.argv[1])
