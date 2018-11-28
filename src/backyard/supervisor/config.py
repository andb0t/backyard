import os
import logging

from yaml import load

import pkg_resources


class Config:
    _instance = None
    _analyzers = []
    _scanners = {}

    def __init__(self):
        scanner_path = pkg_resources.resource_filename("backyard", "supervisor/config/scanner.d")
        for (dirpath, _, filenames) in os.walk(scanner_path):
            for filename in filenames:
                if filename.endswith('.yaml'):
                    self._load_scanner(os.sep.join([dirpath, filename]))

        analyzer_path = pkg_resources.resource_filename("backyard", "supervisor/config/analyzer.d")
        for (dirpath, _, filenames) in os.walk(analyzer_path):
            for filename in filenames:
                if filename.endswith('.yaml'):
                    self._load_analyzer(os.sep.join([dirpath, filename]))

    def get_scanners(self):
        return self._scanners

    def get_analyzers(self):
        return self._analyzers

    def _load_analyzer(self, path):
        with open(path, 'r') as f:
            obj = load(f)
            analyzer = obj.get('analyzer')
            scanners = []
            _scanners = analyzer.get('scanners')
            for scanner in _scanners:
                if scanner in self._scanners:
                   scanners.append(scanner)
                else:
                    logging.warning('unknown scanner %s - skipping', scanner)

            self._analyzers.append({
                'id': analyzer.get('id'),
                'name': analyzer.get('name'),
                'description': analyzer.get('description'),
                'image': analyzer.get('image'),
                'scanners': scanners
             })

    def _load_scanner(self, path):
        with open(path, 'r') as f:
            obj = load(f)
            scanner = obj.get('scanner')
            self._scanners[scanner.get('id')] = {
                'name': scanner.get('name'),
                'description': scanner.get('description'),
                'image': scanner.get('image'),
             }

    @staticmethod
    def get_instance():
        if not Config._instance:
            Config._instance = Config()
        return Config._instance
