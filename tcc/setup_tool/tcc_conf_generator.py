import os.path

from tcc.setup_tool.lib.tcc_operator import TccOpenapi
from tcc.setup_tool.source_of_truth_generator import get_sot_file_path, get_overwrite_file_path, get_template_directory_path
from tcc.setup_tool.cluster_config_handler import ClusterConfigHandler
from common.logger import logger
import yaml
from tcc.setup_tool.lib.helper import Util
import sys
import argparse


def generate_tcc_conf(cluster, service, prod_env=False):
    source_of_truth_path = get_sot_file_path(cluster)
    overwrite_file_path = get_overwrite_file_path(cluster, service)
    template_dir_path = get_template_directory_path(service)
    curr_dir = os.path.dirname(__file__)
    if prod_env:
        cmd = "helm template -f {} -f {} {} --output-dir {}/tmp".format(
            source_of_truth_path,
            overwrite_file_path,
            template_dir_path,
            curr_dir)

    else:
        use_gray_env_value = "use_gray_env=true"
        cmd = "helm template -f {} -f {} --set {} {} --output-dir {}/tmp".format(
            source_of_truth_path,
            overwrite_file_path,
            use_gray_env_value,
            template_dir_path,
            curr_dir)

    logger.info("开始生成TCC配置，执行的命令是：%s" % cmd)
    tcc_directory = os.path.join(curr_dir, "tmp/{}/templates/tcc.yaml".format(service))
    # Remove file if exist
    if os.path.exists(tcc_directory):
        os.remove(tcc_directory)
    with os.popen(cmd) as process:
        output = process.read()
        logger.info(output)

    if not os.path.exists(tcc_directory):
        raise Exception("helm creation failed.")


    return os.path.join(curr_dir, "tmp/{}/templates/tcc.yaml".format(service))


def find_diff_between_gen_and_tcc(cluster, service, update_tcc=False, prod_env=False):
    logger.info("Finding diff for {} {}".format(cluster, service))
    # gen_tcc_path = "/data02/home/jianyu.kok/AeolusSetupTools/tcc/setup_tool/tmp/{}/templates/tcc.yaml".format(service)
    gen_tcc_path = generate_tcc_conf(cluster, service, prod_env)
    tcc_f = open(gen_tcc_path, "r")
    helm_kv = yaml.safe_load(tcc_f)
    config = ClusterConfigHandler.get_config(cluster)
    service_config = config.get_all_services()[service]
    conf_space = service_config.tcc_conf_space_gray
    if prod_env:
        conf_space = service_config.tcc_conf_space
    tcc_open_api = TccOpenapi(
        config.tcc_base_domain,
        service_config.tcc_region,
        service_config.tcc_psm,
        conf_space,
        jwt_base_url=config.jwt_base_url,
        jwt_secret_key=config.jwt_secret_key,
        token=service_config.tcc_token_v2,
        version=service_config.tcc_version,
    )
    tcc_kv = tcc_open_api.get_all_kv()
    logger.info("TCC metadata:")
    logger.info("psm: {}".format(service_config.tcc_psm))
    logger.info("region: {}".format(service_config.tcc_region))
    logger.info("conf_space: {}".format(conf_space))
    logger.info("Start of tcc update list:")
    # Check if existing tcc keys are going to be updated.
    for k in tcc_kv.keys():
        if k in helm_kv.keys():
            if not Util.diff_value(tcc_kv[k], helm_kv[k]):
                if update_tcc:
                    tcc_open_api.update_config(k, helm_kv[k])
                    logger.info("\033[32m " + k + ": 被修改 {} --> {} \033[0m".format(tcc_kv[k], helm_kv[k]))
                else:
                    logger.info("\033[32m " + k + ": 将会被修改 {} --> {} \033[0m".format(tcc_kv[k], helm_kv[k]))
        else:
            logger.info("\033[32m " + k + ": 将会被删除 \033[0m")
            # Don't operate delete
            logger.info("\033[32m " + k + ": 为了安全，不操作删除 \033[0m")

    for k in helm_kv.keys():
        if k not in tcc_kv.keys():
            if update_tcc:
                tcc_open_api.create_config(k, helm_kv[k])
                logger.info("\033[32m " + k + " 将新增。 value: {} \033[0m".format(helm_kv[k]))
            else:
                logger.info("\033[32m " + k + " 将会新增。 value: {} \033[0m".format(helm_kv[k]))

    logger.info("End of tcc update list")


# if __name__ == "__main__":
#     generate_tcc_conf("euttp", "aeolus")
#     generate_tcc_conf("euttp", "ajs")
#     generate_tcc_conf("euttp", "ars")
#     generate_tcc_conf("euttp", "eventhub")
#     generate_tcc_conf("euttp", "meta_service")
#     generate_tcc_conf("euttp", "prepare")
#     generate_tcc_conf("euttp", "vqs")

# if __name__ == "__main__":
    # generate_tcc_conf("idpipo", "sqlquery")
    # find_diff_between_gen_and_tcc("idpipo", "sqlquery", prod_env=True, update_tcc=True)
    # find_diff_between_gen_and_tcc("euttp", "ajs")
    # find_diff_between_gen_and_tcc("euttp", "ars")
    # find_diff_between_gen_and_tcc("euttp", "eventhub")
    # find_diff_between_gen_and_tcc("euttp", "meta_service")
    # find_diff_between_gen_and_tcc("euttp", "prepare")
    # find_diff_between_gen_and_tcc("euttp", "vqs")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cluster", help="cluster to check TCC for e.g. euttp", required=True)
    parser.add_argument("-s", "--service", help="service to check TCC for e.g. aeolus, prepare", required=True)
    # store_true is not used to support dynamic selection of the following 2 values in
    # bytecycle pipeline.
    parser.add_argument("-u", "--update-tcc", help="boolean to determine to update tcc", choices=["true", "false"], type=str.lower)
    parser.add_argument("-p", "--prod-env", help="boolean to determine to update prod environment (will update gray by default)", choices=["true", "false"], type=str.lower)

    args = parser.parse_args()
    logger.info("Running tcc_conf_generator with config")
    logger.info("cluster: {}".format(args.cluster))
    logger.info("service: {}".format(args.service))
    if args.update_tcc == "true":
        args.update_tcc = True
    else:
        args.update_tcc = False
    logger.info("update-tcc: {}".format(args.update_tcc))
    if args.prod_env == "true":
        args.prod_env = True
    else:
        args.prod_env = False
    logger.info("prod-env: {}".format(args.prod_env))
    find_diff_between_gen_and_tcc(args.cluster, args.service, update_tcc=args.update_tcc, prod_env=args.prod_env)
