import requests
from oauthlib.oauth2 import BackendApplicationClient, MissingTokenError
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

from up42 import host


class ProjectKeyToken:
    def __init__(self, project_id: str, project_api_key: str):
        self.project_id = project_id
        self.project_api_key = project_api_key

    def get_value(self):
        try:
            client = BackendApplicationClient(client_id=self.project_id, client_secret=self.project_api_key)
            auth = HTTPBasicAuth(self.project_id, self.project_api_key)
            get_token_session = OAuth2Session(client=client)
            token_response = get_token_session.fetch_token(token_url=host.endpoint("/oauth/token"), auth=auth)
        except MissingTokenError as err:
            raise ValueError("Authentication was not successful, check the provided project credentials.") from err

        return token_response["data"]["accessToken"]


class UserToken:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def get_value(self):
        try:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }
            req_body = {
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
            }
            token_response = requests.post(
                url=host.endpoint("/oauth/token"),
                data=req_body,
                headers=headers,
                timeout=120,
            )
            if token_response.status_code != 200:
                raise ValueError(
                    f"Authentication failed with status code {token_response.status_code}."
                    "Check the provided credentials."
                )
            return token_response.json()["data"]["accessToken"]
        except requests.exceptions.RequestException as err:
            raise ValueError(
                "Authentication failed due to a network error. Check the provided credentials and network connectivity."
            ) from err
