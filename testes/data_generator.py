#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'tardis'

from jinja2 import Environment, FileSystemLoader
import unicodecsv as csv
import random
from testes import CONF
import uuid
from testes import utils
import json
import datetime


class DataGenerator(object):
    def __init__(self):
        self.gen_index_prefix = CONF.gen_index_prefix
        self.gen_index_type = CONF.gen_index_type
        self.env = Environment(loader=FileSystemLoader(CONF.template_dir))

    def _get_index_name(self):
        t = self.gen_index_type
        if t == 'day':
            return '%s-%s' % (CONF.index_prefix, datetime.datetime.utcnow().strftime('%Y-%m-%d'))
        elif t == 'hour':
            return '%s-%s' % (CONF.index_prefix, datetime.datetime.utcnow().strftime('%Y-%m-%d-%H'))
        else:
            return self.gen_index_prefix

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

    def get_query_data(self, tem_name=None, query_data_name=None):

        if tem_name is None:
            tem_name = CONF.template_name
        if query_data_name is None:
            query_data_name = CONF.query_data_name

        data_dict = self._get_data('%s/%s' % (CONF.test_data_dir, query_data_name))
        data_dict = self._get_rand_data(data_dict)

        return self._render(tem_name, data_dict)

    def _gen_create_data(self):
        api_key, api_secret, image_best, image_idcard, request_id = str(uuid.uuid4()), str(uuid.uuid4()), str(
            uuid.uuid4()), \
                                                                    str(uuid.uuid4()), str(uuid.uuid4())
        id_card = utils.random_int(18)
        confidence = random.uniform(1, 100)
        time_used = random.randint(1, 10000)
        timestamp = datetime.datetime.utcnow().isoformat()
        name = '测试-%s' % str(uuid.uuid4())

        data = '{"create":{"_index":"%(index)s","_type":"%(type)s"}}\n' % {'index': self._get_index_name(),
                                                                           'type': CONF.index_type_name}

        data += '{"api_key":"%(api_key)s","api_secret":"%(api_key)s","idcard":"%(id_card)s",' \
                '"image_best":"%(image_best)s","image_idcard":"%(image_idcard)s",' \
                '"method":"%(method)s","name":"%(name)s","path":"%(path)s",' \
                '"response":{"request_id":"%(request_id)s",' \
                '"result_idcard":{"confidence":%(confidence)s,"thresholds":%(thresholds)s},' \
                '"time_used":%(time_used)s},"status_code":%(status_code)s,"timestamp":"%(timestamp)s"}\n'

        status_codes = [200, 201, 202, 400, 401, 404, 402]
        method = ['POST', 'GET', 'DELETE', 'PUT', 'HEAD', 'GET']
        path = ['/verify', '/extract', '/compare']

        data_dict = {'api_key': api_key, 'api_secret': api_secret, 'image_best': image_best,
                     'image_idcard': image_idcard, 'request_id': request_id, 'id_card': id_card,
                     'confidence': confidence,
                     'time_used': time_used,
                     'timestamp': timestamp, 'name': name,
                     'status_code': utils.random_list(status_codes),
                     'method': utils.random_list(method),
                     'path': utils.random_list(path),
                     'thresholds': json.dumps(
                         {'ie-3': random.uniform(1, 100), '1e-4': random.uniform(1, 100),
                          '1e-5': random.uniform(1, 100)})}

        return data % data_dict

    def create_bulk_test_data(self, n, to_file=True):
        data = ''
        for i in xrange(n):
            data += self._gen_create_data(to_file)

        if to_file:
            with open('%s/create_data_%s'(CONF.test_data_dir % n), 'w') as f:
                f.write(data)

        return data
