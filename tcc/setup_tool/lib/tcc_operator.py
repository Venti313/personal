# -*- coding: utf-8 -*-
import logging
import time

from tcc.setup_tool.lib.tcc_operator_v2 import TccOpenapiV2
from tcc.setup_tool.lib.tcc_operator_v3 import TccOpenapiV3

from common.jwt import JWTApiClient

class TccOpenapi():
    def __init__(self, domain, region, psm, confspace, jwt_base_url='', jwt_secret_key='', token='', version='V3'):
        self.domain = domain
        self.region = region
        self.psm = psm
        self.confspace = confspace
        self.token = token
        self.version = version.upper()
        if self.version.upper() == "V3":
            self.jwt_api_client = JWTApiClient(jwt_base_url)
            self.jwt_secret_key = jwt_secret_key
            self.jwt_token = self.jwt_api_client.get_jwt_token(jwt_secret_key)


    def get_all_kv(self):
        if self.version == "V3":
            kv = TccOpenapiV3(domain=self.domain, region=self.region, psm=self.psm, jwt_token=self.jwt_token,
                              confspace=self.confspace).get_all_kv()
        else:
            kv = TccOpenapiV2(domain=self.domain, region=self.region, psm=self.psm, token=self.token,
                              confspace=self.confspace).get_all_kv()
        return kv

    def get_keys(self):
        if self.version == "V3":
            kv = TccOpenapiV3(domain=self.domain, region=self.region, psm=self.psm, jwt_token=self.jwt_token,
                              confspace=self.confspace).get_all_kv()
            return kv.keys()
        else:
            return TccOpenapiV2(domain=self.domain, region=self.region, psm=self.psm, token=self.token,
                              confspace=self.confspace).get_all_keys()

    def create_config(self, key, value):
        if self.version == "V3":
            res = TccOpenapiV3(domain=self.domain, region=self.region, psm=self.psm, jwt_token=self.jwt_token,
                              confspace=self.confspace).create_config(conf_name=key, value=value)
        else:
            res = TccOpenapiV2(domain=self.domain, region=self.region, psm=self.psm, token=self.token,
                              confspace=self.confspace).add_conf(key=key, value=value)
        if res != "None":
            time.sleep(1)
            return True
        else:
            return False

    def delete_config(self, key):
        if self.version == "V3":
            res = TccOpenapiV3(domain=self.domain, region=self.region, psm=self.psm, jwt_token=self.jwt_token,
                               confspace=self.confspace).delete_config(conf_name=key)
        else:
            res = TccOpenapiV2(domain=self.domain, region=self.region, psm=self.psm, token=self.token,
                               confspace=self.confspace).delete_conf(key=key)
        if res != "None":
            time.sleep(1)
            return True
        else:
            logging.info("%s 删除失败", key)
            return False

    def update_config(self, key, value):
        if self.version == "V3":
            res = TccOpenapiV3(domain=self.domain, region=self.region, psm=self.psm, jwt_token=self.jwt_token,
                               confspace=self.confspace).update_config(conf_name=key, value=value)
        else:
            res = TccOpenapiV2(domain=self.domain, region=self.region, psm=self.psm, token=self.token,
                               confspace=self.confspace).modify_reload(key=key, value=value)
        if res != "None":
            time.sleep(1)
            return True
        else:
            return False

    def get_config(self, conf_name):
        if self.version == "V3":
            res = TccOpenapiV3(domain=self.domain, region=self.region, psm=self.psm, jwt_token=self.jwt_token,
                               confspace=self.confspace).get_config(conf_name)
        else:
            res = TccOpenapiV2(domain=self.domain, region=self.region, psm=self.psm, token=self.token,
                               confspace=self.confspace).get_conf_detail(conf_name)
        return res
