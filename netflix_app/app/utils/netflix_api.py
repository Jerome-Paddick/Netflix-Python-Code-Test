import requests
from ..config import Config

class NetflixClient:
    def __init__(self):
        config = Config()
        "Game%20of%20Thrones"
        self.protocol = config.API_PROTOCOL
        self.api_key = config.API_KEY
        self.address = config.API_ADDRESS
        self.port = config.API_PORT
        self.verify_ssl_cert = config.API_VERIFY_SSL_CERT

        self.requester = requests.Session()
        # self.requester.auth = (conf['username'], conf['password'])

    def get(self, params):
        formatted_url = f"{self.protocol}://{self.address}:{self.port}"
        params.update({'apikey': self.api_key})
        response = self.requester.get(formatted_url, params=params, verify=self.verify_ssl_cert)
        return response

