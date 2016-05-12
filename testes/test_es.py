# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'tardis'

from locust import HttpLocust, TaskSet, task
import uuid
import random
import datetime
import utils
import json
from testes.data_generator import DataGenerator
from testes import CONF


def get_index_name(t=None):
    if t == 'day':
        return '%s-%s' % (CONF.index_prefix, datetime.datetime.utcnow().strftime('%Y-%m-%d'))
    elif t == 'hour':
        return '%s-%s' % (CONF.index_prefix, datetime.datetime.utcnow().strftime('%Y-%m-%d-%H'))
    else:
        return CONF.index_prefix


def test_bulk_create(l=None, data=None):
    if l is None:
        import requests
        l = requests
        url = '%s/_bulk' % CONF.host
    else:
        url = '/_bulk'

    if data is None:
        data_path = CONF.test_data_dir + '/create_data_' + str(CONF.test_doc_size)
        with open(data_path, 'r') as f:
            data = f.read()

    l.post(url, data=data, headers={'Content-Type': 'application/octet-stream'})


def _gen_create_data(fixed=False):
    api_key, api_secret, image_best, image_idcard, request_id = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()), \
                                                                str(uuid.uuid4()), str(uuid.uuid4())
    id_card = utils.random_int(18)
    confidence = random.uniform(1, 100)
    time_used = random.randint(1, 10000)
    timestamp = datetime.datetime.utcnow().isoformat()
    name = '测试-%s' % str(uuid.uuid4())

    if not fixed:
        data = '{"create":{"_index":"%(index)s","_type":"%(type)s","_id":"%(id)s"}}\n' % {
            'index': get_index_name('hour'),
            'type': CONF.index_type_name,
            'id': request_id}

        data += '{"api_key":"%(api_key)s","api_secret":"%(api_key)s","idcard":"%(id_card)s",' \
                '"image_best":"%(image_best)s","image_idcard":"%(image_idcard)s",' \
                '"method":"%(method)s","name":"%(name)s","path":"%(path)s",' \
                '"response":{"request_id":"%(request_id)s",' \
                '"result_idcard":{"confidence":%(confidence)s,"thresholds":%(thresholds)s},' \
                '"time_used":%(time_used)s},"status_code":%(status_code)s,"timestamp":"%(timestamp)s"}\n'

    else:
        data = '{"create":{"_index":"%(index)s","_type":"%(type)s"}}\n' % {'index': get_index_name(),
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
                     {'ie-3': random.uniform(1, 100), '1e-4': random.uniform(1, 100), '1e-5': random.uniform(1, 100)})}

    return data % data_dict


def create_bulk_test_data(n, to_file=True):
    data = ''
    for i in xrange(n):
        data += _gen_create_data(to_file)

    if to_file:
        with open('%s/create_data_%s'(CONF.test_data_dir % n), 'w') as f:
            f.write(data)

    return data


def test_query(client, url=None):
    if url is None:
        url = '/faceid-test-2016-05-10-00/_search'

    dg = DataGenerator()
    data = dg.get_query_data()
    return client.get(url, data=data.encode('utf-8'))


test_data = {}


def _load_data():
    if test_data.get(CONF.test_doc_size) is None:
        data_path = CONF.test_data_dir + '/create_data_' + str(CONF.test_doc_size)
        with open(data_path) as f:
            test_data[CONF.test_doc_size] = f.read()


# _load_data()


class ESTask(TaskSet):
    # 批量插入索引
    # @task
    def bulk_create(self):
        data = create_bulk_test_data(CONF.test_doc_size, to_file=False)
        test_bulk_create(self.client, data)

    # 组合查询
    @task
    def query(self):
        test_query(self.client)

    # 简单查询
    # @task
    def query_one(self):
        data = '{"query":{"term":{"idcard":"610460666320295243"}}}'
        self.client.get('/%s/%s/_search' % (get_index_name(), CONF.index_type_name), data=data)

    # 插入单条索引
    # @task
    def create_one(self):
        data = '{"api_key":"9d2b2e57-0cec-420b-8b32-6a02a0e17122","api_secret":"9d2b2e57-0cec-420b-8b32-6a02a0e17122",' \
               '"idcard":"675947879720392855","image_best":"d524075d-f262-45b1-b719-98353ed78eaa",' \
               '"image_idcard":"c3974147-9a33-4a27-b0eb-5681a636ab7a",' \
               '"method":"PUT","name":"测试-9e33dd8b-4c6e-4bad-82c5-b96a4740cd87","path":"/extract",' \
               '"response":{"request_id":"21f334d9-4c2e-4b79-885d-687cc37098be","result_idcard":{"confidence":31.6229458243,' \
               '"thresholds":{"ie-3": 32.38287889944902, "1e-5": 45.97277584826741, "1e-4": 42.01700919162666}},"time_used":5113},"status_code":402,"timestamp":"2016-05-06T03:08:51.848402"}'
        return self.client.post('/%s/%s' % (get_index_name(), CONF.index_type_name), data=data)


class ESLocust(HttpLocust):
    task_set = ESTask
