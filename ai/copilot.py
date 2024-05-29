import json
import os
from tempfile import tempdir
import time
import uuid
import requests
import uuid
import reactivex as rx
from reactivex import operators as ops
import tempfile
# from ai.util import safe_get_element_by_index


def safe_get_element_by_index(lst, index):
    if index < 0 or index >= len(lst):
        return None
    return lst[index]


cache = None

copilot_auth_cache = tempfile.gettempdir() + "/copilot-auth-cache.json"
try:
    if os.path.exists(copilot_auth_cache):
        with open(copilot_auth_cache) as f:
            cache = json.load(f)
except:
    pass


def check_expiry():
    global cache
    if cache is None:
        return
    if cache.get('expires_at', 0) < time.time():
        cache = None


def get_authorization_from_token(copilot_token):
    """When obtaining the Authorization, first attempt to retrieve it from the cache. If it is not available in the cache, retrieve it through an HTTP request and then set it in the cache."""
    global cache
    check_expiry()
    if cache is None:
        get_authorization_url = "https://api.github.com/copilot_internal/v2/token"
        client = requests.Session()
        req = requests.Request("GET", get_authorization_url)
        req.headers["Authorization"] = "token " + copilot_token
        req.headers["User-Agent"] = "GitHubCopilotChat/0.8.0"
        response = client.send(req.prepare())
        response.raise_for_status()

        new_authorization = response.json()
        if new_authorization["token"] == "":
            msg = "Get GithubCopilot Authorization Token Failed, Token is empty"
            return "", response.status_code, msg

        cache = new_authorization
        with open(copilot_auth_cache, "w") as f:
            json.dump(new_authorization, f)
        return cache, response.status_code, ""

    return cache, 200, ""


def copilot_chat_completions(
    auth_token: str,
    messages,
    temperature=0.0,
    model="gpt-4"
):
    token, _, _ = get_authorization_from_token(auth_token)
    url = "https://api.githubcopilot.com/chat/completions"

    req = requests.post(url, headers={
        "Authorization":         "Bearer " + token["token"],
        "X-Request-Id":          str(uuid.uuid4()),
        "Vscode-Sessionid":      str(uuid.uuid4()),
        "Vscode-Machineid":      str(uuid.uuid4()),
        "Editor-Version":        "vscode/1.83.1",
        "Editor-Plugin-Version": "copilot-chat/0.8.0",
        "Openai-Organization":   "github-copilot",
        "Openai-Intent":         "conversation-panel",
        "Content-Type":          "text/event-stream; charset=utf-8",
        "User-Agent":            "GitHubCopilotChat/0.8.0",
        "Accept":                "text/event-stream; charset=utf-8",
        "Accept-Encoding":       "gzip,deflate,br",
        "Connection":            "close",
    }, stream=True, data=json.dumps({
        "messages": messages,
        "model": "gpt-4",
        # turbo not supported? That sucks.
        # "model": model,  # "gpt-4",
        "temperature": float(temperature),
        # "top_p": 1,
        # "n": 1,
        "stream": True,
    }))
    return rx.from_iterable(req.iter_lines(decode_unicode=True)).pipe(
        ops.filter(lambda x: x.startswith("data:") and x[6:].startswith("{")),
        ops.map(lambda x: json.loads(x[6:])),
        ops.map(lambda x: x.get('choices', [])),
        ops.map(lambda x: safe_get_element_by_index(x, 0) or {}),
        ops.map(lambda x: x.get('delta', {})),
        ops.map(lambda x: x.get('content', "")),
        ops.filter(lambda x: x != "" and x is not None),
    )
