import os
from typing import Dict, Optional, List

import yaml
from pydantic import BaseModel, Field

# Cluster Config example
'''
frontend:
    component:
        scm: [REFER TO ScmConfig]
        maat: [REFER TO MaatConfig]
backend:
    component:
        scm: [REFER TO ScmConfig]
        tce: [REFER TO TceConfig]
'''


class ScmComponentConfig(BaseModel):
    scm_repo: str


class MaatComponentConfig(BaseModel):
    maat_publish_region: str
    maat_name: str
    maat_token: str
    maat_gray_name: str
    maat_publish_type: str
    maat_publish_type_gray: str
    maat_parent_name: Optional[str] = ""


class TceComponentConfig(BaseModel):
    tce_psm: str
    tce_psm_cluster_name: str
    tce_psm_cluster_name_gray: str
    tce_psm_cluster_region: str


class TccComponentConfig(BaseModel):
    tcc_cluster: str


class FrontendService(BaseModel):
    scm: ScmComponentConfig
    maat: MaatComponentConfig


class BackendService(BaseModel):
    scm: ScmComponentConfig
    tce: TceComponentConfig
    tcc: Optional[TccComponentConfig] = Field(default=None)


class FrontendServices(BaseModel):
    aeolus_fe: Optional[FrontendService] = Field(default=None)
    fe_prep: Optional[FrontendService] = Field(default=None)
    vscreen: Optional[FrontendService] = Field(default=None)
    queryeditor: Optional[FrontendService] = Field(default=None)
    aeolus_h5: Optional[FrontendService] = Field(default=None)


class BackendServices(BaseModel):
    aeolus: Optional[BackendService] = Field(default=None)
    prepare: Optional[BackendService] = Field(default=None)
    meta_service: Optional[BackendService] = Field(default=None)
    vqs: Optional[BackendService] = Field(default=None)
    bdb_backend: Optional[BackendService] = Field(default=None)
    bdb_jobserver: Optional[BackendService] = Field(default=None)
    bdb_scheduler: Optional[BackendService] = Field(default=None)
    ars: Optional[BackendService] = Field(default=None)
    aeolus_glue: Optional[BackendService] = Field(default=None)
    sqlquery: Optional[BackendService] = Field(default=None)


class PushServices(BaseModel):
    eventhub: Optional[BackendService] = Field(default=None)
    ajs: Optional[BackendService] = Field(default=None)
    subscription: Optional[BackendService] = Field(default=None)
    subscription_push_script: Optional[BackendService] = Field(default=None)
    notification: Optional[BackendService] = Field(default=None)


class ClusterConfig(BaseModel):
    frontend: Optional[FrontendServices] = Field(default=None)
    backend: Optional[BackendServices] = Field(default=None)
    push: Optional[PushServices] = Field(default=None)

    def get_all_frontend_services(self) -> Dict[str, FrontendService]:
        fe_services = {}
        for key in self.frontend.model_fields.keys():
            value = getattr(self.frontend, key)
            if value:
                fe_services[key] = value

        return fe_services

    def get_all_backend_services(self) -> Dict[str, BackendService]:
        be_services = {}
        for key in self.backend.model_fields.keys():
            value = getattr(self.backend, key)
            if value:
                be_services[key] = value

        return be_services

    def get_all_push_services(self) -> Dict[str, BackendService]:
        push_services = {}
        for key in self.push.model_fields.keys():
            value = getattr(self.push, key)
            if value:
                push_services[key] = value

        return push_services


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

    data = ClusterConfigHandler.get_config("pipo")
    logger.info(data.frontend.model_fields.items())
