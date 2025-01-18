import logging

import requests
from requests.auth import HTTPProxyAuth

logging.basicConfig(
    filename='tinder_bio.log',  # Log file name
    level=logging.INFO,  # Log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Log format
)


class TinderConfig:
    API_URL = "https://api.gotinder.com"

    def __init__(
            self,
            token,
            host=None,
            port=None,
            username=None,
            password=None,
            proxy_type=None,
    ):
        self.token = token
        self.proxy = host
        self.proxy_port = port
        self.proxy_username = username
        self.proxy_password = password
        self.proxy_type = proxy_type

    def get_profile(self):
        url = f"{self.API_URL}/profile"
        headers = {"X-Auth-Token": self.token, "Content-Type": "application/json"}
        proxies = (
            {
                "http": f"{self.proxy_type}://{self.proxy}:{self.proxy_port}",
                "https": f"{self.proxy_type}://{self.proxy}:{self.proxy_port}",
            }
            if self.proxy
            else None
        )
        auth = (
            HTTPProxyAuth(self.proxy_username, self.proxy_password)
            if self.proxy
            else None
        )
        try:
            response = requests.get(
                url, headers=headers, proxies=proxies, auth=auth, timeout=40
            )
            return response.json()
        except Exception as e:
            logging.error(f"Error getting profile: {e}")
            return None

    def update_profile(self, bio=None, age_filter_min=None, age_filter_max=None, distance_filter=None):
        url = f"{self.API_URL}/profile"
        headers = {"X-Auth-Token": self.token, "Content-Type": "application/json"}
        if not bio:
            data = {"age_filter_min": age_filter_min, "age_filter_max": age_filter_max,
                    "distance_filter": distance_filter}
        elif not age_filter_min:
            data = {"bio": bio, "age_filter_max": age_filter_max, "distance_filter": distance_filter}
        elif not age_filter_max:
            data = {"bio": bio, "age_filter_min": age_filter_min, "distance_filter": distance_filter}
        elif not distance_filter:
            data = {"bio": bio, "age_filter_min": age_filter_min, "age_filter_max": age_filter_max}
        else:
            data = {"bio": bio, "age_filter_min": age_filter_min, "age_filter_max": age_filter_max,
                    "distance_filter": distance_filter}

        proxies = (
            {
                "http": f"{self.proxy_type}://{self.proxy}:{self.proxy_port}",
                "https": f"{self.proxy_type}://{self.proxy}:{self.proxy_port}",
            }
            if self.proxy
            else None
        )
        auth = (
            HTTPProxyAuth(self.proxy_username, self.proxy_password)
            if self.proxy
            else None
        )
        try:
            response = requests.post(
                url, headers=headers, json=data, proxies=proxies, auth=auth, timeout=40
            )
            return response.json()
        except Exception as e:
            logging.error(f"Error updating profile: {e}")
            return None
