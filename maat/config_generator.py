from typing import Dict, Any, List

from configs.cluster_config_class import ClusterConfig
from configs.config_generator import ConfigGeneratorInterface
from common.logger import logger
from configs.version_config_class import VersionConfig

from scm.config_generator import ScmConfigGenerator

MAAT = "maat"
MAAT_NAME = "maat_name"
MAAT_TOKEN = "maat_token"
MAAT_GRAY_NAME = "maat_gray_name"
MAAT_PUBLISH_TYPE = "maat_publish_type"
MAAT_PUBLISH_TYPE_GRAY = "maat_publish_type_gray"
MAAT_PARENT_NAME = "maat_parent_name"
MAAT_PUBLISH_REGION = "maat_publish_region"
USE_PROD_ENV = "use_prod_env"


# MaatConfigGenerator parse_config will return a config of
# {
#   "aeolus_fe": {
#     "scm_repo": "data/dp/aeolus_fe_eu_ttp",
#     "scm_repo_branch": "release-aeolus-2.60.1",
#     "maat_name": "aeolus-eu-ttp",
#     "maat_token": "315123df6a",
#     "maat_parent_name": "",
#     "maat_publish_region": "US-EastRed",
#     "maat_publish_type": "gray",
#     "maat_gray_name": "gray"
#   }
# }
class MaatConfigGenerator(ConfigGeneratorInterface):
    def __init__(self, use_prod_env: bool = False):
        # Requires SCM config in TCE.
        self.scm_config_gen = ScmConfigGenerator(get_frontend=True)
        self.use_prod_env = use_prod_env

    def parse_config(self, cluster_data: ClusterConfig, version_data: VersionConfig) -> Dict[str, Any]:
        # Pre-requisite:
        # cluster_data and version_data both contain the exact same components.
        # cluster_data for all component contains SCM and SCM_REPO, TCE, TCE_PSM, TCE_PSM_CLUSTER_NAME and TCE_PSM_CLUSTER_NAME_GRAY
        # version_data for all component contains SCM and SCM_REPO_BRANCH
        final_config = self.scm_config_gen.parse_config(cluster_data, version_data)

        clusters = cluster_data.get_all_frontend_services()
        for component_name in final_config.keys():
            component_data = clusters[component_name]
            final_config[component_name][MAAT_NAME] = component_data.maat.maat_name
            final_config[component_name][MAAT_TOKEN] = component_data.maat.maat_token
            final_config[component_name][MAAT_PARENT_NAME] = component_data.maat.maat_parent_name
            final_config[component_name][MAAT_PUBLISH_REGION] = component_data.maat.maat_publish_region
            if self.use_prod_env:
                final_config[component_name][MAAT_PUBLISH_TYPE] = component_data.maat.maat_publish_type
            else:
                final_config[component_name][MAAT_PUBLISH_TYPE] = component_data.maat.maat_publish_type_gray
                final_config[component_name][MAAT_GRAY_NAME] = component_data.maat.maat_gray_name

        return final_config


if __name__ == "__main__":
    conf_gen = MaatConfigGenerator()
    logger.info(conf_gen.generate_config("euttp", "2.60.1_test"))
