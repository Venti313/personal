from typing import Dict, Any, List

from configs.cluster_config_class import ClusterConfig
from configs.config_generator import ConfigGeneratorInterface
from common.logger import logger
from common.utils import find_map_key_intersect
from configs.version_config_class import VersionConfig

TCC = "tcc"
TCC_CLUSTER = "tcc_cluster"
TCC_SERVICE = "tcc_service"
USE_PROD_ENV = "use_prod_env"


# TccConfigGenerator parse_config will return a config of
# {
#   "aeolus": {
#     "tcc_cluster": "euttp",
#     "tcc_service": "aeolus",
#     "use_prod_env": False
#   }
# }
class TccConfigGenerator(ConfigGeneratorInterface):
    def __init__(self, get_backend: bool = False, get_push: bool = False, use_prod_env: bool = False):
        self.get_backend = get_backend
        self.get_push = get_push
        self.use_prod_env = use_prod_env

    def parse_config(self, cluster_data: ClusterConfig, version_data: VersionConfig) -> Dict[str, Any]:
        # Pre-requisite:
        # cluster_data and version_data both contain the exact same components.
        # cluster_data for all component contains SCM and SCM_REPO
        # version_data for all component contains SCM and SCM_REPO_BRANCH
        final_config = {}

        if self.get_backend:
            cluster_services = cluster_data.get_all_backend_services()
            for service, cluster in cluster_services.items():
                if cluster.tcc:
                    final_config[service] = {
                        TCC_CLUSTER: cluster.tcc.tcc_cluster,
                        TCC_SERVICE: service,
                        USE_PROD_ENV: self.use_prod_env
                    }

        if self.get_push:
            cluster_services = cluster_data.get_all_push_services()
            for service, cluster in cluster_services.items():
                if cluster.tcc:
                    final_config[service] = {
                        TCC_CLUSTER: cluster.tcc.tcc_cluster,
                        TCC_SERVICE: service,
                        USE_PROD_ENV: self.use_prod_env
                    }

        return final_config


if __name__ == "__main__":
    conf_gen = TccConfigGenerator()
    logger.info(conf_gen.generate_config("euttp", "2.60.1_test"))
