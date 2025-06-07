import requests
from typing import Optional, Dict, Any, Union, List
from common.logger import logger

class JWTApiClient():
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_jwt_token(self, token):
        path = "/auth/api/v1/jwt"
        if not token:
            raise Exception("token not provided")
        headers = {
            "Authorization": "Bearer {}".format(token)
        }
        response = self.make_request(path, "GET", None, headers)
        if "X-Jwt-Token" not in response.headers:
            logger.info("jwt token not retrieved. Please check /auth/api/v1/jwt' API call. Response = {}".format(response))
            raise Exception("jwt token not retrieved. Please check /auth/api/v1/jwt' API call")

        return response.headers["X-Jwt-Token"]

    def make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Optional[requests.Response]:
        url = self.base_url + endpoint
        response = None

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
                return response
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {e}")
            return None


# Example usage:
if __name__ == "__main__":
    # Initialize the API client with the base URL
    api_client = JWTApiClient(base_url="https://cloud.b.net")

    print(api_client.get_jwt_token("123"))
