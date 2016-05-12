#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'tardis'

from jinja2 import Environment, FileSystemLoader
import unicodecsv as csv
import random
from testes import CONF


class DataGenerator(object):
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(CONF.template_dir))

    def _render(self, tem_name, data):
        template = self.env.get_template(tem_name)
        return template.render(data)

    def _get_data(self, csv_path):
        with open(csv_path, 'r') as infile:
            reader = csv.reader(infile)
            if reader:
                keys = []
                is_first = True
                data_dict = {}
                for row in reader:
                    if is_first:
                        keys = row
                        is_first = False
                        for k in keys:
                            data_dict[k] = []

                    else:
                        for i in xrange(len(keys)):
                            data_dict[keys[i]].append(row[i])

                return data_dict

    def _get_rand_data(self, data_dict):
        new_data_d = {}
        for k, v in data_dict.iteritems():
            new_data_d[k] = v[random.randint(0, len(v) - 1)]
        return new_data_d

    def get_query_data(self):
        data_dict = self._get_data('%s/%s' % (CONF.query_data_dir, CONF.query_data_name))
        data_dict = self._get_rand_data(data_dict)
        return self._render(CONF.template_name, data_dict)


if __name__ == '__main__':
    import requests

    dg = DataGenerator()
    data = dg.get_query_data()
    resp = requests.get('http://10.101.2.20:9200/faceid-test/_search',
                        data=data.encode('utf-8'))
    print resp.content
