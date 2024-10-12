import os
from reactivex import operators as ops

from ai.models import send_message
from ai.util import fit_history
from ai.env import openai_env

def _msg(role, content):
    return {"role": role, "content": content}


def request(query, history):
    _history = history + [_msg("user", query)]
    h = fit_history(_history, max_tokens=openai_env["max_tokens"], model_max_tokens=openai_env["model_max_tokens"])

    response = send_message(
        system=openai_env["system_prompt"],
        messages=h,
        temperature=openai_env["temperature"],
        model=openai_env["model"],
        max_tokens=openai_env["max_tokens"],
    )

    return response.pipe(
        ops.filter(lambda x: x != ""),
    )
