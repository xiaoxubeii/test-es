#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'tardis'

from testes import CONF
from testes.data_generator import DataGenerator
from locust import TaskSet, task


class ESTestCase(TaskSet):
    index_type = CONF.index_type
    index_name = CONF.index_name
    index_gen_type = CONF.index_gen_type
    host = CONF.host
    test_data_dir = CONF.test_data_dir
    test_create_data = CONF.create_data_name
    dg = DataGenerator()
    bulk_create_td = None
    create_td = None
    query_one_data = None

    @classmethod
    def prepare_resource(cls):
        cls.create_td = '{"api_key":"9d2b2e57-0cec-420b-8b32-6a02a0e17122","api_secret":"9d2b2e57-0cec-420b-8b32-6a02a0e17122",' \
                        '"idcard":"675947879720392855","image_best":"d524075d-f262-45b1-b719-98353ed78eaa",' \
                        '"image_idcard":"c3974147-9a33-4a27-b0eb-5681a636ab7a",' \
                        '"method":"PUT","name":"测试-9e33dd8b-4c6e-4bad-82c5-b96a4740cd87","path":"/extract",' \
                        '"response":{"request_id":"21f334d9-4c2e-4b79-885d-687cc37098be","result_idcard":{"confidence":31.6229458243,' \
                        '"thresholds":{"ie-3": 32.38287889944902, "1e-5": 45.97277584826741, "1e-4": 42.01700919162666}},"time_used":5113},' \
                        '"status_code":402,"timestamp":"2016-05-06T03:08:51.848402"}'

        data_path = '%s/%s' % (cls.test_data_dir, cls.test_create_data)
        with open(data_path, 'r') as f:
            cls.bulk_create_td = f.read()

        cls.query_one_data = '{"query":{"term":{"idcard":"610460666320295243"}}}'

    @classmethod
    def _get_url(cls, *args):
        url = '%s/%s/%s' % (cls.host, cls.index_name, cls.index_type)
        for v in args:
            url += '/' + v
        return url

    @task
    def test_create(self):
        url = self._get_url()
        self.client.post(url, data=self.create_td)

    @task
    def test_bulk_create(self):
        url = self._get_url('_bulk')
        self.client.post(url, data=self.bulk_create_td, headers={'Content-Type': 'application/octet-stream'})

    @task
    def test_query_one(self):
        url = self._get_url('_search')
        self.client.get(url, data=self.query_one_data)

    @task
    def test_query(self):
        url = self._get_url('_search')
        data = self.dg.get_query_data()
        self.client.get(url, data=data.encode('utf-8'))

    @task
    def test_agg(self):
        url = self._get_url('_search')
        data = self.dg.get_query_data('agg.tem', 'agg_data.csv')
        self.client.get(url, data=data.encode('utf-8'))


ESTestCase.prepare_resource()
