from common.bytecycle import ByteCycleAPIClient
from common.logger import logger
from scm.config_generator import ScmConfigGenerator
from tcc.setup_tool.tcc_conf_generator import find_diff_between_gen_and_tcc
from tce.config_generator import TceConfigGenerator
from maat.config_generator import MaatConfigGenerator
from tcc.config_generator import TccConfigGenerator

SCM_UPGRADE_PIPELINE_ID = 175327804162
TCE_UPGRADE_PIPELINE_ID = 176980443650
ONE_CLICK_UPGRADE_PIPELINE_ID = 173807692290
TCC_UPGRADE_PIPELINE_ID = 183045766146
ONE_CLICK_UPGRADE_PIPELINE_PUSH_ID = 287731479298

EUTTP_ONE_CLICK_UPGRADE_PIPELINE_ID = 313443196162
EUTTP_ONE_CLICK_UPGRADE_PIPELINE_PUSH_ID = 313443196162

def RunSCMPipeline(cluster, version, username, use_prod_env=False):
    api_client = ByteCycleAPIClient(base_url="https://bi1.net", username=username)
    scm_config_gen = ScmConfigGenerator(get_frontend=True, get_backend=True)
    config = scm_config_gen.generate_config(cluster, version)
    api_client.run_pipeline(SCM_UPGRADE_PIPELINE_ID, config)


def RunTCEUpgradePipeline(cluster, version, username, use_prod_env=False):
    api_client = ByteCycleAPIClient(base_url="https://bi1.net", username=username)
    scm_config_gen = ScmConfigGenerator()
    tce_config_gen = TceConfigGenerator(get_backend=True, use_prod_env=use_prod_env)
    maat_config_gen = MaatConfigGenerator(use_prod_env=use_prod_env)
    config = tce_config_gen.generate_config(cluster, version)
    api_client.run_pipeline(TCE_UPGRADE_PIPELINE_ID, config)


def RunTCCUpgradePipeline(cluster, version, username, use_prod_env=False):
    api_client = ByteCycleAPIClient(base_url="https://bi1.net", username=username)
    tcc_config_gen = TccConfigGenerator(use_prod_env=use_prod_env, get_backend=True)
    config = tcc_config_gen.generate_config(cluster, version)
    api_client.run_pipeline(TCC_UPGRADE_PIPELINE_ID, config)


def RunOneClickUpgradePipeline(cluster, version, username, use_prod_env=False):
    pipeline_id = ONE_CLICK_UPGRADE_PIPELINE_ID
    if cluster in ["euttp", "pipo", "no"]:
        pipeline_id = EUTTP_ONE_CLICK_UPGRADE_PIPELINE_ID

    api_client = ByteCycleAPIClient(base_url="https://bit1.net", username=username)
    scm_config_gen = ScmConfigGenerator(get_frontend=True, get_backend=True)
    tce_config_gen = TceConfigGenerator(get_backend=True, use_prod_env=use_prod_env)
    maat_config_gen = MaatConfigGenerator(use_prod_env=use_prod_env)
    tcc_config_gen = TccConfigGenerator(get_backend=True, use_prod_env=use_prod_env)
    config = {
        "scm": scm_config_gen.generate_config(cluster, version),
        "tce": tce_config_gen.generate_config(cluster, version),
        "frontend": maat_config_gen.generate_config(cluster, version),
        "tcc": tcc_config_gen.generate_config(cluster, version)
    }
    # logger.info(config)
    api_client.run_pipeline(pipeline_id, config)

def RunOneClickUpgradePipelinePush(cluster, version, username, use_prod_env=False):
    if not use_prod_env:
        logger.error("One Click upgrade for push currently only supports prod env.")

    api_client = ByteCycleAPIClient(base_url="https://bi1.net", username=username)
    scm_config_gen = ScmConfigGenerator(get_push=True)
    tce_config_gen = TceConfigGenerator(get_push=True, use_prod_env=use_prod_env)
    tcc_config_gen = TccConfigGenerator(get_push=True, use_prod_env=use_prod_env)
    config = {
        "scm": scm_config_gen.generate_config(cluster, version),
        "tce": tce_config_gen.generate_config(cluster, version),
        "tcc": tcc_config_gen.generate_config(cluster, version)
    }
    # logger.info(config)
    api_client.run_pipeline(ONE_CLICK_UPGRADE_PIPELINE_PUSH_ID, config)

def RunLocallyTCCUpgrade(cluster, update_tcc, use_prod_env):
    # find_diff_between_gen_and_tcc(cluster, "aeolus", update_tcc=update_tcc, prod_env=use_prod_env)
    # find_diff_between_gen_and_tcc(cluster, "prepare", update_tcc=update_tcc, prod_env=use_prod_env)
    # find_diff_between_gen_and_tcc(cluster, "meta_service", update_tcc=update_tcc, prod_env=use_prod_env)
    # find_diff_between_gen_and_tcc(cluster, "vqs", update_tcc=update_tcc, prod_env=use_prod_env)
    # find_diff_between_gen_and_tcc(cluster, "ajs", update_tcc=update_tcc, prod_env=use_prod_env)
    # find_diff_between_gen_and_tcc(cluster, "ars", update_tcc=update_tcc, prod_env=use_prod_env)
    find_diff_between_gen_and_tcc(cluster, "eventhub", update_tcc=update_tcc, prod_env=use_prod_env)
    # find_diff_between_gen_and_tcc(cluster, "sqlquery", update_tcc=update_tcc, prod_env=use_prod_env)

if __name__ == "__main__":
    RunOneClickUpgradePipeline("mycis", "mycis_2.70.0", "jianyu.kok", True)
    # RunLocallyTCCUpgrade("no", False, False)
    # RunLocallyTCCUpgrade("no", True, False)
    # RunLocallyTCCUpgrade("no", True, True)
    # RunOneClickUpgradePipeline("uspipo",
    #                            "uspipo_2.66.0",
    #                            "jianyu.kok",
    #                            use_prod_env=True)

    # RunOneClickUpgradePipelinePush("uspipo",
    #                            "uspipo_2.66.0",
    #                            "jianyu.kok",
    #                            use_prod_env=True)

    # RunOneClickUpgradePipeline("euttp",
    #                            "euttp_2.64.0",
    #                            "jianyu.kok",
    #                            use_prod_env=False)

