from itertools import dropwhile
import os
import reactivex as rx
from reactivex import operators as ops
from math import ceil

from ai.models import send_message

_openai_env = {
    "model_max_tokens": int(os.environ.get("CHATGPT_CLI_OPENAI_MODEL_MAX_TOKENS", "4000")),
    "max_tokens": int(os.environ.get("CHATGPT_CLI_OPENAI_RESPONSE_MAX_TOKENS", "1000")),
    "model": os.environ.get("CHATGPT_CLI_OPENAI_MODEL", "gpt-3.5-turbo"),
    "temperature": float(os.environ.get("CHATGPT_CLI_OPENAI_TEMPERATURE", "0.3")),
    "system_prompt": os.environ.get("CHATGPT_CLI_OPENAI_SYSTEM_PROMPT", "You answer briefly and to the point.")
}


def _msg(role, content):
    return {"role": role, "content": content}


def _fit_history(history, limit):
    def _count_tokens(str):
        return max(ceil(len(str) / 4), 1)

    # Extra leeway because token counter is rough on the edges.
    limit -= limit * 0.2
    out = []
    for msg in reversed(history):
        if limit <= 0:
            break
        t = _count_tokens(msg["content"])
        limit -= t
        out.insert(0, msg)
    return list(dropwhile(lambda t: t['role'] != 'user', out))


def request(query, history):
    tokens = _openai_env["model_max_tokens"] - _openai_env["max_tokens"]
    _history = history + [_msg("user", query)]
    h = _fit_history(_history, tokens)

    response = send_message(
        system=_openai_env["system_prompt"],
        messages=h,
        temperature=_openai_env["temperature"],
        model=_openai_env["model"],
        max_tokens=_openai_env["max_tokens"],
    )

    return response.pipe(
        ops.filter(lambda x: x != ""),
    )
