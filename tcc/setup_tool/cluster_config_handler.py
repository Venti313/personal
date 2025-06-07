import os
from typing import Dict, Optional, List

import yaml
from pydantic import BaseModel, Field


class Service(BaseModel):
    tcc_token_v2: str
    tcc_psm: str
    tcc_version: str
    tcc_region: str
    tcc_conf_space: str
    tcc_conf_space_gray: str


class Services(BaseModel):
    aeolus: Service
    prepare: Service
    meta_service: Service
    vqs: Service
    ajs: Service
    ars: Service
    eventhub: Service
    sqlquery: Service


class ClusterConfig(BaseModel):
    tcc_base_domain: str
    jwt_base_url: str
    jwt_secret_key: str
    services: Services

    def get_all_services(self) -> Dict[str, Service]:
        services = {}
        for key in self.services.model_fields.keys():
            value = getattr(self.services, key)
            if value:
                services[key] = value

        return services


class ClusterConfigHandler():
    @staticmethod
    def get_config(file_name) -> ClusterConfig:
        config_dir = os.path.dirname(__file__)
        file_path = os.path.join(config_dir, "cluster_configs/{}.yaml".format(file_name))
        if not os.path.exists(file_path):
            raise FileNotFoundError("Cluster config not found '{}'".format(file_path))

        with open(file_path, 'r') as config_file:
            data = yaml.safe_load(config_file)
            config = ClusterConfig(**data)
        return config


if __name__ == "__main__":
    from common.logger import logger

    data = ClusterConfigHandler.get_config("euttp")
    logger.info(data.get_all_services())
