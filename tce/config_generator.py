from typing import Dict, Any, List

from configs.cluster_config_class import ClusterConfig
from configs.config_generator import ConfigGeneratorInterface
from common.logger import logger
from configs.version_config_class import VersionConfig

from scm.config_generator import ScmConfigGenerator

TCE = "tce"
TCE_PSM = "tce_psm"
TCE_PSM_CLUSTER_NAME = "tce_psm_cluster_name"
TCE_PSM_CLUSTER_NAME_GRAY = "tce_psm_cluster_name_gray"
TCE_PSM_CLUSTER_REGION = "tce_psm_cluster_region"
USE_PROD_ENV = "use_prod_env"

# Example output
# {
#   "aeolus": {
#     "scm_repo": "data/dp/aeolus",
#     "scm_repo_branch": "euttp_2.60.1",
#     "tce_psm": "data.aeolus.api_eu_ttp",
#     "tce_psm_cluster_region": "US-East-Red",
#     "tce_psm_cluster_name": "gray"
#   }
# }


class TceConfigGenerator(ConfigGeneratorInterface):
    def __init__(self, get_backend: bool = False, get_push: bool = False, use_prod_env: bool = False):
        # Requires SCM config in TCE.
        self.get_backend = get_backend
        self.get_push = get_push
        self.scm_config_gen = ScmConfigGenerator(get_backend=get_backend, get_push=get_push)
        self.use_prod_env = use_prod_env

    def parse_config(self, cluster_data: ClusterConfig, version_data: VersionConfig) -> Dict[str, Any]:
        # Pre-requisite:
        # cluster_data and version_data both contain the exact same services.
        # cluster_data for all component contains SCM and SCM_REPO, TCE, TCE_PSM, TCE_PSM_CLUSTER_NAME and TCE_PSM_CLUSTER_NAME_GRAY
        # version_data for all component contains SCM and SCM_REPO_BRANCH
        final_config = self.scm_config_gen.parse_config(cluster_data, version_data)

        if self.get_backend:
            services = cluster_data.get_all_backend_services()
            for component_name, component_data in services.items():
                final_config[component_name][TCE_PSM] = component_data.tce.tce_psm
                final_config[component_name][TCE_PSM_CLUSTER_REGION] = component_data.tce.tce_psm_cluster_region
                if self.use_prod_env:
                    final_config[component_name][TCE_PSM_CLUSTER_NAME] = component_data.tce.tce_psm_cluster_name
                else:
                    final_config[component_name][TCE_PSM_CLUSTER_NAME] = component_data.tce.tce_psm_cluster_name_gray

        if self.get_push:
            services = cluster_data.get_all_push_services()
            for component_name, component_data in services.items():
                final_config[component_name][TCE_PSM] = component_data.tce.tce_psm
                final_config[component_name][TCE_PSM_CLUSTER_REGION] = component_data.tce.tce_psm_cluster_region
                if self.use_prod_env:
                    final_config[component_name][TCE_PSM_CLUSTER_NAME] = component_data.tce.tce_psm_cluster_name
                else:
                    final_config[component_name][TCE_PSM_CLUSTER_NAME] = component_data.tce.tce_psm_cluster_name_gray

        return final_config


if __name__ == "__main__":
    conf_gen = TceConfigGenerator()
    logger.info(conf_gen.generate_config("euttp", "2.60.1_test"))
