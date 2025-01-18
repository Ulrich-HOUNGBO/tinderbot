import logging
import random
import time

import requests
from requests.auth import HTTPProxyAuth

logging.basicConfig(
    filename='bot_service.log',  # Log file name
    level=logging.INFO,          # Log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Log format
)

class BotService:
    API_URL = "https://api.gotinder.com"

    USER_AGENT = 'Tinder/13.19.0 (iPhone; iOS 16.6; Scale/3.00)'

    def __init__(
        self,
        token,
            refresh_token=None,
            device_id=None,
        host=None,
        port=None,
        username=None,
        password=None,
            proxy_type=None
    ):
        self.token = token
        self.proxy = host
        self.proxy_port = port
        self.proxy_username = username
        self.proxy_password = password
        self.proxy_type = proxy_type

    def get_proxies(self):
        if self.proxy and self.proxy_type:
            proxy_url = f"{self.proxy_type.lower()}://{self.proxy}:{self.proxy_port}"
            return {"http": proxy_url, "https": proxy_url}
        return None

    def retry_request(self, url, headers, proxies, auth, max_retries=3, timeout=40):
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, proxies=proxies, auth=auth, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)
        return {"error": "Max retries exceeded"}

    def create_error_response(self, message):
        logging.error(message)
        return {"error": message}

    def connect_tinder(self):
        url = f"{self.API_URL}/profile"
        headers = {"X-Auth-Token": self.token, "user-agent": self.USER_AGENT}
        proxies = self.get_proxies()
        auth = HTTPProxyAuth(self.proxy_username, self.proxy_password) if self.proxy else None

        logging.info(f"Connecting to Tinder API with proxies: {proxies}")
        try:
            response = requests.get(url, headers=headers, proxies=proxies, auth=auth, timeout=40)
            response.raise_for_status()
            return {"success": True} if response.status_code == 200 else {"error": response.text}
        except requests.RequestException as e:
            logging.error(f"Failed to connect to Tinder API: {e}")
            return {"error": str(e)}

    def swipe(self, user_id, swipe_right=True):
        url = f"{self.API_URL}/{'like' if swipe_right else 'pass'}/{user_id}"
        headers = {"X-Auth-Token": self.token, "Content-Type": "application/json", "user-agent": self.USER_AGENT}
        proxies = self.get_proxies()
        auth = HTTPProxyAuth(self.proxy_username, self.proxy_password) if self.proxy else None
        try:
            response = requests.get(
                url, headers=headers, proxies=proxies, auth=auth, timeout=40
            )
            if response.status_code == 200:
                logging.info(
                    f"Swipe {'right' if swipe_right else 'left'} on {user_id} succeeded."
                )
                return True
            elif response.status_code == 401:
                logging.error("Unauthorized access. Please check your token.")
                return {"error": "Unauthorized access."}
            else:
                logging.error(
                    f"Failed to swipe on {user_id}. Response: {response.status_code}"
                )
                return {"error": response.text}
        except requests.RequestException as e:
            logging.error(f"Exception during swipe: {str(e)}")
            return {"error": str(e)}

    def automate_swipes_task(self, min_swipes, max_swipes, min_right_swipe_percentage, max_right_swipe_percentage):
        headers = {"X-Auth-Token": self.token, "user-agent": self.USER_AGENT}
        proxies = self.get_proxies()
        auth = HTTPProxyAuth(self.proxy_username, self.proxy_password) if self.proxy else None

        swipe_count = 0
        num_swipes = random.randint(min_swipes, max_swipes)
        right_swipe_percentage = random.uniform(min_right_swipe_percentage, max_right_swipe_percentage)

        logging.info(f"Starting swipe task: {num_swipes} swipes with {right_swipe_percentage:.2f}% right swipes")

        try:
            while swipe_count < num_swipes:
                response = self.retry_request(
                    f"{self.API_URL}/user/recs", headers, proxies, auth, max_retries=3
                )
                if "error" in response:
                    return response

                profiles = response.json().get("results", [])
                if not profiles:
                    logging.warning("No profiles found. Retrying after delay...")
                    time.sleep(30)
                    continue

                for profile in profiles:
                    user_id = profile["_id"]
                    time.sleep(random.uniform(2, 5))  # Simulate viewing time

                    swipe_right = random.random() < (right_swipe_percentage / 100)
                    swipe_result = self.swipe(user_id, swipe_right)

                    if isinstance(swipe_result, dict) and "error" in swipe_result:
                        return swipe_result

                    swipe_count += 1
                    logging.info(f"Swiped {'right' if swipe_right else 'left'} on user {user_id}. Total: {swipe_count}")

                    if swipe_count >= num_swipes:
                        return {"success": True}

                    time.sleep(random.uniform(9, 30))  # Delay between swipes

        except Exception as e:
            logging.error(f"Error during swipe task: {e}")
            return {"error": str(e)}
        return {"success": True, "swipe_count": swipe_count}

    def addBioagraphie(self, bio):
        url = f"{self.API_URL}/profile"
        headers = {"X-Auth-Token": self.token, "Content-Type": "application/json"}
        data = {"bio": bio}
        proxies = (
            {
                "http": f"socks5://{self.proxy}:{self.proxy_port}",
                "https": f"socks5://{self.proxy}:{self.proxy_port}",
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
            if response.status_code == 200:
                logging.info("Bio added successfully.")
                return True
            elif response.status_code == 401:
                logging.error("Unauthorized access. Please check your token.")
                return {"error": "Unauthorized access."}
            else:
                logging.error(f"Failed to add bio. Response: {response.status_code}")
                return {"error": response.text}
        except requests.RequestException as e:
            logging.error(f"Exception during bio addition: {str(e)}")
            return {"error": str(e)}

    def get_profile(self):
        url = f"{self.API_URL}/profile"
        headers = {"X-Auth-Token": self.token}
        proxies = (
            {
                "http": f"socks5://{self.proxy}:{self.proxy_port}",
                "https": f"socks5://{self.proxy}:{self.proxy_port}",
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
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logging.error("Unauthorized access. Please check your token.")
                return {"error": "Unauthorized access."}
            else:
                logging.error(f"Failed to get profile. Response: {response.status_code}")
                return {"error": response.text}
        except requests.RequestException as e:
            logging.error(f"Exception during fetching profile: {str(e)}")
            return {"error": str(e)}

    def generate_new_token(self, refresh_token, device_id):
        url = f"{self.API_URL}/auth"
        headers = {"Content-Type": "application/json", "user-agent": self.USER_AGENT}
        data = {"refresh_token": refresh_token, "device_id": device_id}
        proxies = (
            {
                "http": f"socks5://{self.proxy}:{self.proxy_port}",
                "https": f"socks5://{self.proxy}:{self.proxy_port}",
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
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Failed to generate new token. Response: {response.status_code}")
                return {"error": response.text}
        except requests.RequestException as e:
            logging.error(f"Exception during token generation: {str(e)}")
            return {"error": str(e)}
