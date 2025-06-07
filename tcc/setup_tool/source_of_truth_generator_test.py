import unittest
from tcc.setup_tool.source_of_truth_generator import *


class TestFindSourceOfTruth(unittest.TestCase):
    def test_find_source_of_truth_multiple_sot(self):
        actual_value = "example.com/api/privilege/test_region"
        template_value = "{{ .Values.global.gemini.host }}/api/privilege/{{ .Values.global.gemini.region }}"

        expected_result = {
            "Values.global.gemini.host": "example.com",
            "Values.global.gemini.region": "test_region"
        }

        result = find_source_of_truths(actual_value, template_value)

        self.assertEqual(result, expected_result)

    def test_find_source_of_truth_single_sot(self):
        actual_value = "example.com/api/privilege/test_region"
        template_value = "{{ .Values.global.gemini.host }}"

        expected_result = {
            "Values.global.gemini.host": "example.com/api/privilege/test_region",
        }

        result = find_source_of_truths(actual_value, template_value)

        self.assertEqual(result, expected_result)

    def test_find_source_of_truth_value_has_special_char(self):
        actual_value = "https://er/table_update_status?cluster={}&dbName={}&tableName={}&force={}"
        template_value = "{{ .Values.global.clickhouse_ops.domain }}/clickhouse_ops/api/v1/table_manager/table_update_status?cluster={}&dbName={}&tableName={}&force={}"

        expected_result = {
            "Values.global.clickhouse_ops.domain": "https://clickhouse-i18n.bytedance.net",
        }

        result = find_source_of_truths(actual_value, template_value)

        self.assertEqual(result, expected_result)

    def test_find_source_of_truth_with_brackets(self):
        actual_value = "(.*)https://e_manager/table_update_status?cluster={}&dbName={}&tableName={}&force={}"
        template_value = "(.*){{ .Values.global.clickhouse_ops.domain }}/clickhouse_ops/api/v1/table_manager/table_update_status?cluster={}&dbName={}&tableName={}&force={}"

        expected_result = {
            "Values.global.clickhouse_ops.domain": "https://,
        }

        result = find_source_of_truths(actual_value, template_value)

        self.assertEqual(result, expected_result)


class TestReverseEngineerSourceOfTruth(unittest.TestCase):

    def test_reverse_engineer_source_of_truth(self):
        # Define some sample input data
        tcc_map = {
            'ELASTICSEARCH_CLIENT_INIT_PARAMS': '''{
    "host": "common762-i18n-es.byted.org:80"
}''',
            # Add more key-value pairs as needed
        }
        template_map = {
            "ELASTICSEARCH_CLIENT_INIT_PARAMS": '{"host": {{ .Values.global.es.client_host }}}'
        }

        # Call the function being tested
        sot, overwrite_values = reverse_engineer_source_of_truth(tcc_map, template_map)
        print(sot, overwrite_values)
        # Assert that the returned values are as expected
        expected_sot = {}  # Define your expected source of truth dictionary here
        expected_overwrite_values = {}  # Define your expected overwrite values dictionary here
        self.assertEqual(sot, expected_sot)
        self.assertEqual(overwrite_values, expected_overwrite_values)

class TestFindConditionalSotToTCCKeys(unittest.TestCase):

    def test_find_conditional_sot_to_tcc_keys(self):
        find_conditions_sot_to_tcc_keys("aeolus")


if __name__ == '__main__':
    unittest.main()
