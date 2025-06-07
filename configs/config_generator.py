from abc import ABC, abstractmethod
from typing import Dict, Any, List

from common.logger import logger
from configs.cluster_config_class import ClusterConfigHandler, ClusterConfig
from configs.version_config_class import VersionConfigHandler, VersionConfig


# Interface class for config generator
class ConfigGeneratorInterface(ABC):
    def generate_config(self, cluster: str, version: str) -> Dict[str, Any]:
        # Generating config requires 2 value, cluster and version.
        # cluster value is used to retrieve metadata values of the cluster, e.g. euttp, pipo, sg, va.
        # cluster value will be retrieved from global_config/{cluster}.yaml
        #
        # version is used to retrieve version data the cluster should be upgraded to.
        # E.g. euttp-2.60.1, release-aeolus-2.60.1
        # version data will be retrieved from version_config/{version}.yaml
        cluster_data = ClusterConfigHandler.get_config(cluster)
        version_data = VersionConfigHandler.get_config(version)
        issues = self.config_precheck(cluster_data, version_data)
        # issues = self.config_precheck(cluster_data, version_data)
        if issues:
            logger.error("config precheck failed {}".format(issues))
            raise Exception("config precheck failed {}".format(issues))
        return self.parse_config(cluster_data, version_data)


    def config_precheck(self, cluster_data: ClusterConfig, version_data: VersionConfig) -> List[str]:
        # All versions component must be in cluster component, but not vice versa.
        # e.g.
        # 1. Cluster have aeolus_h5, version don't have --> OK
        # 2. Version have aeolus_h5, cluster don't have --> NOT OK
        errors = []
        cluster_frontend_services = cluster_data.get_all_frontend_services()
        version_frontend_services = version_data.get_all_frontend_services()
        version_frontend_service_keys = set(version_frontend_services.keys())
        # Check that the same frontend components are declared in both cluster and version data.
        for key in version_frontend_service_keys:
            if key not in cluster_frontend_services:
                errors.append("{} missing from cluster config".format(key))
                continue

            cluster_field_value = cluster_frontend_services[key]
            version_field_value = version_frontend_services[key]
            if version_field_value and not cluster_field_value:  # Both have value
                errors.append("{} must be filled in cluster".format(key))

        cluster_backend_services = cluster_data.get_all_backend_services()
        version_backend_services = version_data.get_all_backend_services()
        all_backend_service_keys = set(cluster_backend_services.keys())
        all_backend_service_keys.update(set(version_backend_services.keys()))

        # Check that the same backend components are declared in both cluster and version data.
        for key in all_backend_service_keys:
            if key not in cluster_backend_services:
                errors.append("{} missing from cluster config".format(key))
                continue
            if key not in version_backend_services:
                errors.append("{} missing from version config".format(key))
                continue

            cluster_field_value = cluster_backend_services[key]
            version_field_value = version_backend_services[key]
            if cluster_field_value and version_field_value:  # Both have value
                continue
            elif cluster_field_value is None and version_field_value is None:
                continue
            else:
                errors.append("{} must be filled in both version and cluster".format(key))

        return errors

    @abstractmethod
    def parse_config(self, cluster_data: ClusterConfig, version_data: VersionConfig) -> Dict[str, Any]:
        # parse_config is to be overwritten, it will be used to convert cluster_data and version_data to
        # the format required to execute the upgrade for specific components in bytecycle.
        pass

