import json
from doctest import debug

import requests
from utils import log

def authenticate(config):
    """Authenticate and return access token."""
    client_auth = requests.auth.HTTPBasicAuth(
        config["HTTPBasicAuth1"], config["HTTPBasicAuth2"]
    )
    post_data = {
        "grant_type": "password",
        "username": config["username"],
        "password": config["password"]
    }
    headers = {"User-Agent": config["User-Agent"]}

    if debug:
        log(
            json.dumps({
                'auth': f"{config['HTTPBasicAuth1']}, {config['HTTPBasicAuth2']}",
                'headers': headers,
                'post_data': post_data
            })
        )

    #client_auth = requests.auth.HTTPBasicAuth('Y0csQ993Iek_6k0XMqf4sQ', 'DHYuixLeLmbM2pEjHzvYw6FtPWlZhw')
    #post_data = {"grant_type": "password", "username": "Linore_", "password": "Gliding-Sworn2-Carat"}
    #headers = {"User-Agent": "ChangeMeClient/0.1 by Linore_"}
    response = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=client_auth,
        data=post_data,
        headers=headers
    )
    if debug:
        log(response.json().get("error"))
        log(response.status_code)
    if response.status_code != 200 or response.json().get("error"):
        log(f"Authentication failed: {response.status_code} - {response.reason}, {response.text}")
        return None

    return response.json().get("access_token")

def fetch_saved_items(token, config, after=None):
    """Fetch saved items from Reddit."""
    if debug:
        log(token)
    headers = {
        "Authorization": f"bearer {token}",
        "User-Agent": config["User-Agent"]
    }
    url = f"https://oauth.reddit.com/user/{config['username']}/saved?limit={config['count']}"

    if after:
        url += f"&after={after}"

    log(url)
    response = requests.get(url, headers=headers)
    log(response.json())
    if response.status_code != 200:
        log(f"Failed to fetch saved items: {response.status_code}")
        return None

    return response.json()
