import time
from doctest import debug
from os.path import exists

import requests
import mimetypes

from config_manager import ConfigManager
from logger import log
from pathlib import Path

from utils import get_gallery

class RedditDownloader:
    def __init__(self, config_manager: ConfigManager, existing_items):
        self.debug = config_manager.debug
        self.token = ""
        self.config_manager = config_manager
        self.existing_items = existing_items
        self.target_folder = Path(config_manager.target_path)
        self.authenticate()


    def authenticate(self):
        if not self.config_manager.token:
            return self.send_authenticate_request(self.config_manager)
        if time.time() > float(self.config_manager.expiration_ts):
            return self.send_authenticate_request(self.config_manager)
        return self.config_manager.token


    @staticmethod
    def send_authenticate_request(config_manager: ConfigManager):
        """Authenticate to the Reddit API."""
        client_auth = requests.auth.HTTPBasicAuth(config_manager.http_basic_auth1, config_manager.http_basic_auth2)
        post_data = {"grant_type": "password", "username": config_manager.username, "password": config_manager.password}
        headers = {"User-Agent": config_manager.user_agent}
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
        if config_manager.debug:
            log(response.text)
        response = response.json()
        config_manager.expiration_ts = time.time() + response["expires_in"]
        config_manager.token = response["access_token"]

    def get_saved_generator(self):
        """Yield saved items from Reddit."""
        after = ""
        count = 0
        while after is not None:
            headers = {"Authorization": "bearer " + self.config_manager.token, "User-Agent": self.config_manager.user_agent}
            request = f"https://oauth.reddit.com/user/{self.config_manager.username}/saved?limit={self.config_manager.count}&sort=new"
            count += self.config_manager.count
            if after:
                request += f"&after={after}&count={count}"
            log(request)
            response = requests.get(request, headers=headers)
            json_data = response.json()
            if self.debug:
                log(json_data)

            pruned_object = self.prune_reddit_object(json_data)

            yield pruned_object
            if len(pruned_object) < self.config_manager.count:
                after = None
            else:
                after = json_data["data"]["after"]



    def exists(self, test_key):
        return any(key == test_key for key in self.existing_items)

    def prune_reddit_object(self, server_items):
        """Filter saved Reddit items."""
        result = []
        if self.debug:
            log(f"Existing items: {self.existing_items}")

        for item in server_items["data"]["children"]:
            item_id = item['data']['id'].strip()  # Strip whitespace if necessary
            if self.debug:
                log(f"Checking ID: {item_id}")
                log(f"Exists: {self.exists(item_id)}")
            exists = self.exists(item_id)
            if exists:
                if self.debug:
                    log("Item exists: " + item_id)
                continue
            try:
                image_obj = {
                    "id": item["data"]["id"],
                    "url": item["data"]["url"],
                    "permalink": item["data"]["permalink"],
                    "ts": item["data"]["created_utc"],
                    "nsfw": item["data"]["over_18"],
                    "title": item["data"]["title"],
                    "subreddit": item["data"]["subreddit"],
                    "is_gallery": "is_gallery" in item["data"],
                    "sub_items": get_gallery(item["data"]) if "is_gallery" in item["data"] else []
                }
                result.append(image_obj)
            except Exception as e:
                log(f"Error filtering saved item: {str(e)}")
        return result

