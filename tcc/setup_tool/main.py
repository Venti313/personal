from common.logger import logger
from lib.tcc_operator import TccOpenapi
from cluster_config_handler import ClusterConfigHandler


if __name__ == "__main__":
    logger.info("TEST")
    config = ClusterConfigHandler.get_config("pipo")
    logger.info(config)
    tcc_open_api = TccOpenapi(
        config.tcc_base_domain,
        config.services.aeolus.tcc_region,
        config.services.aeolus.tcc_psm,
        "prod",
        token=config.services.aeolus.tcc_token_v2,
        version=config.services.aeolus.tcc_version,
        jwt_secret_key=config.jwt_secret_key,
        jwt_base_url=config.jwt_base_url
    )
    output = tcc_open_api.get_all_kv()
    logger.info(output)
