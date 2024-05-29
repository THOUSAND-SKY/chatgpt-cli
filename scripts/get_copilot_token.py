#!/usr/bin/env python3

# Stole this from this repo:
# https://github.com/aaamoon/copilot-gpt4-service

import requests
import re
import os
import sys
from enum import Enum
import typing
import time
PROXY = {
    "http": "",
    "https": ""
}


try:
    import requests
except ImportError:
    print("requests is not installed, please install it by running `pip install requests`")
    sys.exit(1)


class LoginError(Enum):
    AUTH_PENDING = 1
    EXPIRED_TOKEN = 2
    NETWORK_ERROR = 3
    OTHER_ERROR = 4


HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
}


def getLoginInfo(proxy=None) -> (LoginError, typing.Union[dict, Exception]):
    url = "https://github.com/login/device/code"
    body = {
        "client_id": "Iv1.b507a08c87ecfe98",
        "scope": "read:user"
    }

    try:
        resp = requests.post(url, headers=HEADERS,
                             json=body, proxies=proxy, timeout=10)
    except requests.exceptions.ConnectionError:
        return LoginError.NETWORK_ERROR, None
    except Exception as e:
        return LoginError.OTHER_ERROR, e
    return None, resp.json()


def pollAuth(device_code: str, proxy=None) -> (LoginError, str):
    url = "https://github.com/login/oauth/access_token"
    body = {
        "client_id": "Iv1.b507a08c87ecfe98",  # client_id of gh copilot
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
    }

    try:
        resp = requests.post(url, headers=HEADERS,
                             json=body, proxies=proxy, timeout=10)
    except requests.exceptions.ConnectionError:
        return LoginError.NETWORK_ERROR, None
    except Exception as e:
        return LoginError.OTHER_ERROR, e

    data = resp.json()

    if data.get("error") == "authorization_pending":
        return LoginError.AUTH_PENDING, None
    if data.get("error") == "expired_token":
        return LoginError.EXPIRED_TOKEN, None
    elif "access_token" in data:
        return None, data["access_token"]
    else:
        return LoginError.OTHER_ERROR, data


def getToken(proxy=None) -> (LoginError, str):
    # get login info
    err, login_info = getLoginInfo(proxy)
    if err is not None:
        if err == LoginError.NETWORK_ERROR:
            print("network error, please check your network.")
        elif err == LoginError.OTHER_ERROR:
            print("unknown error occurred when getting login info.")
            print("error message:", login_info)
        return err, None

    interval = login_info['interval']
    print(
        f"Please open {login_info['verification_uri']} in browser and enter {login_info['user_code']} to login.")
    # poll for auth status
    while True:
        err, access_token = pollAuth(login_info['device_code'], proxy)
        if err is None:
            return None, access_token
        elif err == LoginError.AUTH_PENDING:
            pass
        elif err == LoginError.EXPIRED_TOKEN:
            print("session expired, please try again.")
            return err, None
        elif err == LoginError.NETWORK_ERROR:
            print("network error, please check your network.")
            return err, None
        elif err == LoginError.OTHER_ERROR:
            print("unknown error occurred when pulling auth info.")
            print("error message:", access_token)
            return err, None
        time.sleep(interval)


if __name__ == "__main__":
    for k, v in PROXY.items():
        if v == "":
            PROXY[k] = os.getenv(f"{k}_proxy".upper()) or os.getenv(
                f"{k}_proxy".lower()) or ""
            if re.match(r"^.+://.+$", PROXY[k]) is None and PROXY[k] != "":
                PROXY[k] = "http://" + PROXY[k]
    err, token = getToken(PROXY)
    if err is None:
        print("Your token is:")
        print(token)
