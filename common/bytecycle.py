import json

import requests
from typing import Optional, Dict, Any, Union, List
from common.jwt import JWTApiClient
from common.logger import logger


class ByteCycleAPIClient():
    def __init__(self, base_url: str, username: str):
        self.base_url = base_url
        self.jwt_api_client = JWTApiClient(base_url="https://1.com")
        self.service_account_secret = "123456"
        self.username = username

    def get_pipelines(self, space_id: int, pipeline_ids: List[int] = None, page_size: int = 10, page_num: int = 1):
        path = "/api/v1/pipelines/open"
        params = {
            "space_id": space_id,
            "pipeline_ids": pipeline_ids,
            "page_size": page_size,
            "page_num": page_num,
        }

        return self.make_request(path, "GET", params)

    def run_pipeline(self, pipeline_id: int, custom_vars: Dict[str, Union[str, int, bool, Dict]], callback_url: str = ""):
        path = "/api/v1/pipelines/open/{}/run".format(pipeline_id)
        pipeline_custom_vars = []
        for key, value in custom_vars.items():
            if isinstance(value, bool):
                var_value = {
                    "boolean": value
                }
            elif isinstance(value, int):
                var_value = {
                    "number": value
                }
            elif isinstance(value, str):
                var_value = {
                    "text": value
                }
            elif isinstance(value, Dict):
                var_value = {
                    "text": json.dumps(value)
                }
            else:
                raise Exception("unsupported value {}".format(value))
            pipeline_custom_vars.append({
                "name": "custom.{}".format(key),  # Have to manually attach custom prefix.
                "value": var_value
            })
        data = {}
        if pipeline_custom_vars:
            data["custom_vars"] = pipeline_custom_vars
        if callback_url:
            data["callback_url"] = callback_url
        return self.make_request(path, "POST", data)

    def make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        url = self.base_url + endpoint
        response = None
        jwtToken = self.jwt_api_client.get_jwt_token(self.service_account_secret)
        if not headers:
            headers = {}
        if "x-jwt-token" not in headers:
            headers["x-jwt-token"] = jwtToken
        if "username" not in headers:
            headers["username"] = self.username
        try:
            if method == 'GET':
                response = requests.get(url, params=data, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, json=data, headers=headers)

            # Check for successful response (status code 200)
            if response.status_code == 200:
                logger.info("ByteCycleApiClient API Call Successful: {} {} {}".format(url, data, response.json()))
                return response.json()
            else:
                logger.error(f"Error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request Exception: {e}")
            return None


# Example usage:
if __name__ == "__main__":
    # Initialize the API client with the base URL
    api_client = ByteCycleAPIClient(base_url="https://bits.b.net")

    logger.info(api_client.get_pipelines(4084924930))
