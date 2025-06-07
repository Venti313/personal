# -*- coding: utf-8 -*-

import requests
import logging
import json

from .helper import Util, retry_on_failure

level = logging.INFO
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=level, format=LOG_FORMAT)

class TccOpenapiV2():

    def __init__(self, domain, region, psm, confspace, token):
        self.domain = domain
        self.region = region
        self.psm = psm
        self.confspace = confspace
        self.token = token

    # 获取所有的key
    @retry_on_failure(max_retries=3, delay=2)
    def get_all_keys(self):
        url = self.domain + "/api/v2/open/config/all_keys"
        params = {
            "service_name": self.psm,
            "region": self.region,
            "confspace": self.confspace,
            "online_only": True,
            "token": self.token,
            "app_name": ""
        }
        res = requests.get(url=url, params=params, verify=False)
        if res.status_code == 200 and json.loads(res.text)["error_code"] == 0:
            return json.loads(res.text)['data']
        else:
            logging.info(res.text)
            return None

    # 修改配置并直接发布
    @retry_on_failure(max_retries=3, delay=2)
    def modify_reload(self, key, value, note=""):
        url = self.domain + "/api/v2/open/config/modify"
        header = {
            "Content-Type": "application/json",
            "tcc-openapi-mock": "0"  #置1，用于测试，表示此次请求是mock请求，不会触发真实修改；置0或不填，则会触发真实修改
        }
        value_type, value = Util.value_to_str(value)
        params = {
            "service_name": self.psm,
            "data": {
                "region": self.region,
                "confspace": self.confspace,
                "key": key,
                "value": value,
                "from_version": 0,
                "note": note
            },
            "token": self.token,
            "app_name": ""
        }
        res = requests.post(url=url, headers=header, json=params)
        if res.status_code == 200 and json.loads(res.text)["error_code"] == 0:
            return json.loads(res.text)['data']
        else:
            logging.info(res.text)
            return None

    # 修改配置不直接发布
    @retry_on_failure(max_retries=3, delay=2)
    def modify_only(self, key, value, note=""):
        url = self.domain + "/api/v2/open/config/modify_only"
        headers = {
            "Content-Type": "application/json",
            "tcc-openapi-mock": "1"  #置1，用于测试，表示此次请求是mock请求，不会触发真实修改；置0或不填，则会触发真实修改
        }
        value_type, value = Util.value_to_str(value)
        params = {
            "service_name": self.psm,
            "data": {
                "region": self.region,
                "confspace": self.confspace,
                "key": key,
                "value": value,
                "from_version": 0,
                "note": note
            },
            "token": self.token,
            "app_name": ""
        }
        res = requests.post(url=url, headers=headers, json=params)
        if res.status_code == 200 and json.loads(res.text)["error_code"] == 0:
            return json.loads(res.text)['data']
        else:
            logging.info(res.text)
            return None

    # 添加配置
    @retry_on_failure(max_retries=3, delay=2)
    def add_conf(self, key, value):
        url = self.domain + "/api/v2/open/config/create"
        headers = {
            "Content-Type": "application/json"
        }
        value_type, value = Util.value_to_str(value)
        params = {
            "service_name": self.psm,
            "data": {
                "region": self.region,
                "confspace": self.confspace,
                "key": key,
                "value": value,
                "value_type": value_type,
                "description": "",
                "tag": "",
                "enable_cdn": False
                },
            "token": self.token,
            "app_name": ""
        }
        res = requests.post(url=url, headers=headers, json=params)
        if res.status_code == 200 and json.loads(res.text)["error_code"] == 0:
            return json.loads(res.text)['data']
        else:
            logging.info(res.text)
            return None

    @retry_on_failure(max_retries=3, delay=2)
    def delete_conf(self, key):
        url = self.domain + "/api/v2/open/config/delete"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "service_name": self.psm,
            "data": {
                "region": self.region,
                "confspace": self.confspace,
                "key": key
            },
            "token": self.token,
            "app_name": ""
        }
        res = requests.post(url=url, headers=headers, json=params)
        if res.status_code == 200 and json.loads(res.text)["error_code"] == 0:
            logging.info(res.text)
            return json.loads(res.text)
        else:
            logging.info(res.text)
            return None

    @retry_on_failure(max_retries=3, delay=2)
    def get_conf_detail(self, key):
        url = self.domain + "/api/v2/open/config/detail"
        params = {
            "service_name": self.psm,
            "region": self.region,
            "confspace": self.confspace,
            "key": key,
            "with_validator": False,  #是否返回验证器validator信息
            "token": self.token,
            "app_name": ""
        }
        res = requests.get(url=url, params=params, verify=False)
        if res.status_code == 200 and json.loads(res.text)["error_code"] == 0:
            res_json = json.loads(res.text)['data']
            key_detail = {"key": res_json["key"], "value": res_json["latest_value"]}
            return key_detail
        else:
            logging.info(res.text)
            return None

    # 每次最多只能获取一百个key的信息，qps<=2
    @retry_on_failure(max_retries=3, delay=2)
    def _get_some_keys_detail(self, keys):
        if len(keys) == 0:
            return []
        url = self.domain + "/api/v2/open/config/details"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "service_name": self.psm,
            "region": self.region,
            "confspace": self.confspace,
            "keys": keys,
            "with_validator": False,
            "token": self.token,
            "app_name": ""
        }
        res = requests.post(url=url, headers=headers, json=params)
        if res.status_code == 200 and json.loads(res.text)["error_code"] == 0:
            return json.loads(res.text)['data']
        else:
            logging.info(res.text)
            return None

    @retry_on_failure(max_retries=3, delay=2)
    def get_all_keys_detail(self):
        keys = self.get_all_keys()
        keys_detail = []
        if len(keys) == 0:
            return keys_detail
        while len(keys) > 100:
            keys_detail.extend(self._get_some_keys_detail(keys[:100]))
            keys = keys[100:]
        keys_detail.extend(self._get_some_keys_detail(keys))
        return keys_detail

    @retry_on_failure(max_retries=3, delay=2)
    def get_all_kv(self):
        all_keys_detail = self.get_all_keys_detail()
        kv = {}
        for item in all_keys_detail:
            kv.update({item['key']: item['online_value']})
        return kv