from typing import Dict, Any, List

from configs.cluster_config_class import ClusterConfig
from configs.config_generator import ConfigGeneratorInterface
from common.logger import logger
from common.utils import find_map_key_intersect
from configs.version_config_class import VersionConfig

SCM = "scm"
SCM_REPO = "scm_repo"
SCM_REPO_BRANCH = "scm_repo_branch"


# ScmConfigGenerator parse_config will return a config of
# {
#   "aeolus_fe": {
#     "scm_repo": "data/dp/aeolus_fe_eu_ttp",
#     "scm_repo_branch": "release-aeolus-2.60.1"
#   },
#   "aeolus": {
#     "scm_repo": "data/dp/aeolus",
#     "scm_repo_branch": "euttp_2.60.1"
#   }
# }
class ScmConfigGenerator(ConfigGeneratorInterface):
    def __init__(self, get_frontend: bool = False, get_backend: bool = False, get_push: bool = False):
        self.get_frontend = get_frontend
        self.get_backend = get_backend
        self.get_push = get_push
        if not self.get_frontend and not self.get_backend and not self.get_push:
            raise Exception("ScmConfigGenerator must at least get 1 of frontend, backend and push")

    def parse_config(self, cluster_data: ClusterConfig, version_data: VersionConfig) -> Dict[str, Any]:
        # Pre-requisite:
        # cluster_data and version_data both contain the exact same components.
        # cluster_data for all component contains SCM and SCM_REPO
        # version_data for all component contains SCM and SCM_REPO_BRANCH
        final_config = {}

        if self.get_frontend:
            cluster_services = cluster_data.get_all_frontend_services()
            version_services = version_data.get_all_frontend_services()

            # version_services is guaranteed to be a subset of cluster_services but not vice versa
            for service in version_services.keys():
                cluster = cluster_services[service]
                version = version_services[service]
                final_config[service] = {
                    SCM_REPO: cluster.scm.scm_repo,
                    SCM_REPO_BRANCH: version.scm.scm_repo_branch
                }

        if self.get_backend:
            cluster_services = cluster_data.get_all_backend_services()
            version_services = version_data.get_all_backend_services()

            # version_services is guaranteed to be a subset of cluster_services but not vice versa
            for service in version_services.keys():
                cluster = cluster_services[service]
                version = version_services[service]
                final_config[service] = {
                    SCM_REPO: cluster.scm.scm_repo,
                    SCM_REPO_BRANCH: version.scm.scm_repo_branch
                }

        if self.get_push:
            cluster_services = cluster_data.get_all_push_services()
            version_services = version_data.get_all_push_services()

            # version_services is guaranteed to be a subset of cluster_services but not vice versa
            for service in version_services.keys():
                cluster = cluster_services[service]
                version = version_services[service]
                final_config[service] = {
                    SCM_REPO: cluster.scm.scm_repo,
                    SCM_REPO_BRANCH: version.scm.scm_repo_branch
                }

        return final_config


if __name__ == "__main__":
    conf_gen = ScmConfigGenerator()
    logger.info(conf_gen.generate_config("euttp", "euttp_2.64.0"))
