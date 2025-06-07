# -*- coding: utf-8 -*-
import requests
import json

from .helper import Util


class TccOpenapiV3():
    def __init__(self, domain, region, psm, jwt_token, confspace):
        self.domain = domain
        self.region = region
        self.psm = psm
        self.dir = "/" + confspace
        self.header = {
            "Domain": "tcc_v3_openapi",
            "x-jwt-Token": jwt_token,
            "Content-Type": "application/json"
        }

    def create_config(self, conf_name, value):
        url = self.domain + "/bcc/open/config/create"
        value_type, value = Util.value_to_str(value)
        params = {
            "ns_name": self.psm,
            "region": self.region,
            "dir": self.dir,
            "conf_name": conf_name,
            "data_type": value_type,
            "value": value,
            "update_strategy": "modify_and_deploy",
            "operator": "niruntao",
            "description": value
        }
        res = requests.post(headers=self.header, url=url, params=params, verify=False)
        if res.status_code == 200:
            return json.loads(res.text)['data']
        else:
            return None

    def get_config(self, conf_name):
        url = self.domain + "/bcc/open/config/get"
        params = {
            "ns_name": self.psm,
            "region": self.region,
            "dir": self.dir,
            "conf_name": conf_name
        }
        res = requests.get(headers=self.header, url=url, params=params, verify=False)
        if res.status_code == 200:
            res_json = json.loads(res.text)['data']
            key_detail = {"key": res_json['conf_name'], "value": res_json["version_data"]["data"]}
            return key_detail
        else:
            return None

    def update_config(self, conf_name, value, ):
        url = self.domain + "/bcc/open/config/update"
        value_type, value = Util.value_to_str(value)
        params = {
            "ns_name": self.psm,
            "region": self.region,
            "dir": self.dir,
            "conf_name": conf_name,
            "data_type": value_type,
            "value": value,
            "update_strategy": "modify_and_deploy",
            "operator": "jianyu.kok",
            "description": value
        }
        res = requests.post(headers=self.header, url=url, params=params, verify=False)

        if res.status_code == 200:
            return json.loads(res.text)['data']
        else:
            return None

    def delete_config(self, conf_name, ):
        url = self.domain + "/bcc/open/config/delete"
        params = {
            "ns_name": self.psm,
            "region": self.region,
            "dir": self.dir,
            "conf_name": conf_name,
            "update_strategy": "modify_and_deploy",
            "operator": "niruntao"
        }
        res = requests.post(headers=self.header, url=url, params=params, verify=False)
        if res.status_code == 200:
            return json.loads(res.text)['data']
        else:
            return None

    def list_config(self, page=1):
        url = self.domain + "/bcc/open/config/list"
        params = {
            "ns_name": self.psm,
            "region": self.region,
            "dir": self.dir,
            "with_value": True,
            "return_value_strategy": "online_version",
            "operator": "niruntao",
            "page": page,
            "page_size": 100
        }
        res = requests.post(headers=self.header, url=url, params=params, verify=False)
        if res.status_code == 200:
            return json.loads(res.text)
        else:
            return None

    def list_dir(self):
        url = self.domain + "/bcc/open/dir/list"
        params = {
            "ns_name": self.psm
        }
        res = requests.post(headers=self.header, url=url, params=params, verify=False)
        if res.status_code == 200:
            return json.loads(res.text)['data']
        else:
            return None

    def get_namespace(self):
        url = self.domain + "/bcc/open/namespace/get"
        params = {
            "ns_name": self.psm
        }
        res = requests.get(headers=self.header, url=url, params=params, verify=False)
        if res.status_code == 200:
            return json.loads(res.text)['data']
        else:
            return None

    def list_all_config(self):
        kv_detail = []
        page = 1
        total_page = 1
        while page <= total_page:
            res = self.list_config(page)
            kv_detail.extend(res['data']['items'])
            page, total_page = res['page_info']['page'], res['page_info']['total_page']
            page += 1
        return kv_detail

    def get_all_kv(self):
        kv = {}
        kv_detail = self.list_all_config()
        for item in kv_detail:
            kv.update({item['conf_name']: item['version_data']['data']})
        return kv
