import base64
import requests
from datetime import datetime, timedelta


class BadCredentials(Exception):
    def __init__(self):
        super().__init__("Invalid username or password")


class PleasantAPIToken:
    def __init__(self, token_as_json):
        self.access_token = token_as_json["access_token"]
        self._expire_date = datetime.now() + timedelta(seconds=token_as_json["expires_in"])

    @property
    def expired(self):
        return datetime.now() > self._expire_date


class PleasantAPI:
    def __init__(self, url: str, user: str, password: str, verify_https: bool = True):
        self.base_url = url
        self.user = user
        self.password = password
        self.verify_https = verify_https
        self._token = None

        if not self.verify_https:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    @property
    def token(self) -> str:
        if self._token is None or self._token.expired:
            data = {
                "grant_type": "password",
                "username": self.user,
                "password": self.password
            }

            response = requests.get(f'{self.base_url}/oauth2/token', data=data, verify=self.verify_https)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                if response.status_code == 400 and response.json()["error"] == "invalid_grant":
                    raise BadCredentials
                else:
                    raise e
            self._token = PleasantAPIToken(response.json())

        return self._token.access_token

    def _request(self, url: str) -> requests.Response:
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            # https://pleasantsolutions.com/info/pleasant-password-server/x-common-issues#v5APIError500
            "X-Pleasant-Client-Identifier": "7f1b1ccc-747a-4459-bf93-f2a10c24e7a8"
        }

        response = requests.get(url, headers=headers, verify=self.verify_https)
        response.raise_for_status()
        return response

    def get_credential(self, entry_id: str) -> str:
        url = f'{self.base_url}/api/v5/rest/entries/{entry_id}/password'
        return self._request(url).text[1:-1]

    def get_attachment(self, entry_id: str, attachment_id: str) -> bytes:
        url = f"{self.base_url}/api/v5/rest/entries/{entry_id}/attachments/{attachment_id}"
        decoded_file = self._request(url).json()["FileData"]
        return base64.b64decode(decoded_file)

    def get_db(self) -> dict:
        url = f"{self.base_url}/api/v5/rest/folders"
        db_hierarchy_as_json = self._request(url).json()
        return db_hierarchy_as_json
