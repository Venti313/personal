# -*- coding: utf-8 -*-

import os
import logging
import json
import deepdiff
from datetime import date
from shutil import rmtree
import time
import functools



class Util():

    @classmethod
    def value_to_str(cls, value):
        value_type = cls.data_type(value)
        if value_type == 'string':
            value = str(value)
        else:
            if isinstance(value, str):
                value = json.loads(value)
            value = json.dumps(value)
        return value_type, value

    @classmethod
    def data_type(cls, config_value):
        if config_value == "true" or config_value == "True" or config_value == "False" or config_value == "false":
            return "string"
        if isinstance(config_value, dict):
            return "json"
        if isinstance(config_value, bool):
            return "string"
        if isinstance(config_value, list):
            return "json"
        if isinstance(config_value, int):
            return "string"
        if isinstance(config_value, type(None)):
            return "string"
        if isinstance(config_value, date):
            return "string"
        if config_value.isdecimal():
            return "string"
        try:
            json.loads(config_value)
            return "json"
        except Exception as e:
            return "string"

    @classmethod
    def diff_json(cls, local_dict, tcc_dict):
        diff_res = deepdiff.DeepDiff(local_dict, tcc_dict)
        if "dictionary_item_added" in diff_res.keys():
            return False
        if "dictionary_item_removed" in diff_res.keys():
            return False
        if "values_changed" in diff_res.keys():
            return False
        return True

    @classmethod
    def diff_value(cls, local_value, tcc_value):
        local_value_type = cls.data_type(local_value)
        tcc_value_type = cls.data_type(tcc_value)
        if local_value_type == 'int':
            local_tmp = str(local_value)
            return local_tmp == str(tcc_value)

        if local_value_type != tcc_value_type:
            # print("HERE",local_value, tcc_value)
            print(local_value_type, tcc_value_type)
            raise
        if local_value_type == "string":
            if local_value == "true" or local_value == "True":
                return tcc_value == "true" or tcc_value == "True" or tcc_value is True
            if local_value == "False" or local_value == "false":
                return tcc_value == "False" or tcc_value == "false" or tcc_value is False

            return local_value == str(tcc_value)
        if not isinstance(local_value, dict) and not isinstance(local_value, list):
            local_value = json.loads(local_value)
        if not isinstance(tcc_value, dict) and not isinstance(tcc_value, list):
            tcc_value = json.loads(tcc_value)
        return cls.diff_json(local_value, tcc_value)


def retry_on_failure(max_retries=3, delay=1, exceptions=(Exception,)):
    """
    A decorator to retry a function or method call on failure.

    :param max_retries: Maximum number of retries.
    :param delay: Delay between retries in seconds.
    :param exceptions: A tuple of exception classes to catch and retry on.
    :return: The decorated function.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        raise
                    print(f"Attempt {retries} failed with error {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)

        return wrapper

    return decorator
