import json
import os
import re

import yaml

from common.logger import logger
from tcc.setup_tool.cluster_config_handler import ClusterConfigHandler
from tcc.setup_tool.lib.tcc_operator import TccOpenapi

AMBIGUOUS_KEY_TEMPLATE = "{}_POSSIBLE_VALUES_FOUND"

def repr_str(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')
    return dumper.org_represent_str(data)


def merge_dicts(dict1, dict2):
    merged = dict1.copy()
    for key, value in dict2.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_dicts(merged[key], value)
        elif key in merged and value != merged[key]:
            add_ambiguous_key_value(merged, key, value)
        else:
            merged[key] = value
    return merged


def unflatten_dict(dict):
    result = {}
    for key, value in dict.items():
        split_key = key.split('.')
        current_map = result
        for i, k in enumerate(split_key):
            if i == len(split_key) - 1:
                current_map[k] = parse_string_value(value)
            elif k not in current_map:
                current_map[k] = {}
            current_map = current_map[k]
    return result


def add_ambiguous_key_value(dict, key, value):
    key_for_ambiguous_value = AMBIGUOUS_KEY_TEMPLATE.format(key)
    logger.info("ambiguous key found {}, storing all possible values in {}".format(key, key_for_ambiguous_value))
    if key_for_ambiguous_value not in dict:
        dict[key_for_ambiguous_value] = [dict[key]]
    # Add new value into set.
    dict[key_for_ambiguous_value].append(value)
    dict[key] = value


def get_template_directory_path(service):
    curr_dir = os.path.dirname(__file__)
    return os.path.join(curr_dir, "services", service)


def get_tcc_template_file_path(service):
    curr_dir = os.path.dirname(__file__)
    return os.path.join(curr_dir, "services", service, "config", "tcc.yaml")


def get_sot_file_path(cluster):
    curr_dir = os.path.dirname(__file__)
    return os.path.join(curr_dir, "source_of_truth", cluster, "global.yaml")


def get_overwrite_file_path(cluster, service):
    curr_dir = os.path.dirname(__file__)
    return os.path.join(curr_dir, "source_of_truth", cluster, "{}.yaml".format(service))


def get_key_value_from_template(service):
    template_file_path = get_tcc_template_file_path(service)
    with open(template_file_path, 'r') as file:
        file_content = file.read()

    pattern = r'^\s*([^:#\s]+)\s*:\s*["\']?(.*?)["\']?\s*$'
    matches = re.findall(pattern, file_content, re.MULTILINE)

    # Convert matches to dictionary format
    key_value_pairs = {key: value for key, value in matches}

    return key_value_pairs


# This is used to find SOTs that are used in if-else statements for helm.
# E.g.
# {{- if eq .Values.global.lark_app.monitor.enabled "true" }}
# LARK_MONITOR_APP_ID: {{ .Values.global.lark_app.monitor.id }}
# LARK_MONITOR_APP_SECRET: {{ .Values.global.lark_app.monitor.secret }}
# {{- end }}
#
# This function should return the mapping of conditional SOTs with the TCC key.
# 'global.lark_app.monitor.enabled': [LARK_MONITOR_APP_ID, LARK_MONITOR_APP_SECRET]
#
# CURRENT_ASSUMPTION: There will not be a nested if else for SOT conditions.
def find_conditions_sot_to_tcc_keys(service):
    template_file_path = get_tcc_template_file_path(service)
    with open(template_file_path, 'r') as file:
        lines = file.readlines()

    stack = []
    sot_to_tcc_key_map = {}
    for line in lines:
        if_start_match = re.match(r'^\s*{{-\s*if\s*eq\s*\.Values\.(.*?)\s*"true"\s*}}\s*$', line)
        # Should only have 1.
        if if_start_match:
            stack.append(if_start_match.group(1))

        if_end_match = re.match(r'^\s*{{-\s*end\s*}}\s*$', line)
        if if_end_match and stack:
            stack.pop()

        if stack:
            sot = stack[0]
            tcc_key_matches = re.match(r'^(\w*?):', line)
            # Should only have 1 tcc_key per line
            if tcc_key_matches:
                if sot not in sot_to_tcc_key_map:
                    sot_to_tcc_key_map[sot] = []
                sot_to_tcc_key_map[sot].append(tcc_key_matches.group(1))

    return sot_to_tcc_key_map


# conditions_source_of_truths are source of truths that are used in a if-else statement
# in the template file.
def reverse_engineer_conditions_source_of_truths(tcc_map, service):
    sot_to_tcc_keys_map = find_conditions_sot_to_tcc_keys(service)
    sot_map = {}
    for sot, tcc_keys in sot_to_tcc_keys_map.items():
        # value is intentionally set to string
        value = "true"
        for key in tcc_keys:
            if key not in tcc_map:
                # value is intentionally set to string
                value = "false"
                break
        sot_map[sot] = value

    source_of_truth = {}
    for sot_key, sot_value in sot_map.items():
        split_key = sot_key.split('.')
        current_map = source_of_truth
        for i, k in enumerate(split_key):
            if i == len(split_key) - 1:
                current_map[k] = parse_string_value(sot_value)
            elif k not in current_map:
                current_map[k] = {}
            current_map = current_map[k]

    return source_of_truth


def parse_string_value(str_value, return_json_obj=False):
    try:
        # Attempt to parse the value as JSON and dump it back as json str
        # This is done to fix the formatting and prevent excessive escape characters in string.
        json_value = json.loads(str_value)
        if return_json_obj:
            return json_value
        return json.dumps(json_value, ensure_ascii=False)
    except ValueError:
        # If parsing fails, return the original value
        return str_value
    except TypeError:
        # If parsing fails, return the original value
        return str_value


def find_source_of_truths(actual_value, template_value):
    actual_value = parse_string_value(actual_value)
    template_value = parse_string_value(template_value)
    sot_keys = re.findall(r'{{\s*\.Values\.(.*?)\s*}}', template_value)

    # Split string by SOT
    split_template_value = re.split(r'{{\s*\.Values\..*?\s*}}', template_value)
    # Escape the template string, and change all SOT keys to capture group.
    regex_pattern = r'(.*)'.join([re.escape(tv) for tv in split_template_value])
    # Add ^ and $ to ensure that regex pattern spans through entire string.
    regex_pattern = "^" + regex_pattern + "$"
    matches = re.findall(regex_pattern, actual_value)
    sot_map = {}

    if not matches:
        logger.info("No match found for {} and template".format(actual_value, template_value))
        return {}
    for idx, key in enumerate(sot_keys):
        if isinstance(matches[0], tuple):
            value = matches[0][idx]
        else:
            value = matches[idx]

        sot_map[key] = value

    return unflatten_dict(sot_map)


def reverse_engineer_source_of_truth(tcc_map, template_map):
    overwrite_values = {}
    source_of_truth = {}
    for key, value in tcc_map.items():
        if key not in template_map:
            logger.info("KEY {} don't exist in template".format(key))
            # Add to override file
            # ./services/{service}/{cluster}.yaml
            overwrite_values[key] = parse_string_value(value)
            continue
        # Identify source of truth value
        sot_map = find_source_of_truths(value, template_map[key])
        if not sot_map:
            logger.info("no sot found for {}".format(key))
            # Add to overwrite values if value in template is different
            # from TCC value.
            if str(value) != str(template_map[key]):
                overwrite_values[key] = parse_string_value(value)
            continue
        source_of_truth = merge_dicts(source_of_truth, sot_map)

    final_overwrite_values = {
        "extraFileVars": overwrite_values
    }
    return source_of_truth, final_overwrite_values


# The values retrieved here will be injected into the source of truth with
# the highest precedence
def get_source_of_truth_to_inject(cluster):
    config = ClusterConfigHandler.get_config(cluster)
    services = config.get_all_services()
    inject_source_of_truth = {
        "global": {}
    }
    tcc_name_map = {}
    for service_name, service_config in services.items():
        tcc_name_map[service_name] = service_config.tcc_psm
    inject_source_of_truth["global"]["tcc_name"] = tcc_name_map
    return inject_source_of_truth


def generate_source_of_truth(cluster, services):
    # Steps to generate source of truth
    # 1. Get actual TCC KV mappings.
    # 2. Find all KVs required in template
    # 3. {{- if eq .Values.global.lark_app.monitor.enabled "true" }} Check for all these.
    # 3. For Each KVs in template, find the corresponding key in mappings
    # 4. Determine the value.
    # 5. Keep track of all missing KVs in template and/or actual TCC mappings.
    config = ClusterConfigHandler.get_config(cluster)
    final_sot_map = {}
    final_overwrite_map = {}
    # Create a SOT by combining information found in all services TCC.
    for service in services:
        logger.info("Generating source of truth for {}".format(service))
        service_config = config.get_all_services()[service]
        tcc_open_api = TccOpenapi(
            config.tcc_base_domain,
            service_config.tcc_region,
            service_config.tcc_psm,
            service_config.tcc_conf_space,  # always get source of truth from production
            jwt_base_url=config.jwt_base_url,
            jwt_secret_key=config.jwt_secret_key,
            token=service_config.tcc_token_v2,
            version=service_config.tcc_version,
        )
        tcc_map = tcc_open_api.get_all_kv()

        template_map = get_key_value_from_template(service)
        sot, overwrite_values = reverse_engineer_source_of_truth(tcc_map, template_map)

        conditions_sot = reverse_engineer_conditions_source_of_truths(tcc_map, service)
        sot = merge_dicts(sot, conditions_sot)

        final_sot_map = merge_dicts(final_sot_map, sot)
        final_overwrite_map[service] = overwrite_values

    # Inject source of truth into final_sot_map
    sot_to_inject = get_source_of_truth_to_inject(cluster)
    final_sot_map = merge_dicts(final_sot_map, sot_to_inject)

    # Set string to dump multi lines using '|' style, single line with normal style.
    yaml.SafeDumper.org_represent_str = yaml.SafeDumper.represent_str
    yaml.add_representer(str, repr_str, Dumper=yaml.SafeDumper)

    sot_path = get_sot_file_path(cluster)

    with open(sot_path, 'w') as file:
        logger.info("Creating file {}".format(sot_path))
        yaml.safe_dump(final_sot_map, file, allow_unicode=True)

    for service, overwrite_values in final_overwrite_map.items():
        overwrite_path = get_overwrite_file_path(cluster, service)
        with open(overwrite_path, 'w') as file:
            logger.info("Creating file {}".format(overwrite_path))
            yaml.safe_dump(overwrite_values, file, allow_unicode=True)
    # logger.info(sot)
    # logger.info(overwrite_values)


if __name__ == "__main__":
    # In case of ambiguous fields, the last service value will have precedence.
    generate_source_of_truth("pipo", [
        "eventhub",
        "ajs",
        "ars",
        "vqs",
        "prepare",
        "meta_service",
        "aeolus",
    ])
    # find_source_of_truths("example.com/api/privilege/test_region",
    #                       "{{ .Values.global.gemini.host }}/api/privilege/{{ .Values.global.gemini.region }}")
