import os
import openai
import reactivex as rx
from reactivex import operators as ops
from math import ceil

# Set your OpenAI API key here
openai.api_key = os.environ.get("OPENAI_API_KEY")

_openai_env = {
    "model_max_tokens": int(os.environ.get("CHATGPT_CLI_OPENAI_MODEL_MAX_TOKENS", "4000")),
    "max_tokens": int(os.environ.get("CHATGPT_CLI_OPENAI_RESPONSE_MAX_TOKENS", "1000")),
    "model": os.environ.get("CHATGPT_CLI_OPENAI_MODEL", "gpt-3.5-turbo"),
    "temperature": float(os.environ.get("CHATGPT_CLI_OPENAI_TEMPERATURE", "0.5")),
    "system_prompt": os.environ.get("CHATGPT_CLI_OPENAI_SYSTEM_PROMPT", "You are ChatGPT, a large language model trained by OpenAI. You answer briefly and to the point.")
}


def _msg(role, content):
    return {"role": role, "content": content}


_system_context = [_msg(
    "system", _openai_env["system_prompt"])]


def _fit_history(history, limit):
    def _count_tokens(str):
        return max(ceil(len(str) / 4), 1)

    # Extra 500 char leeway because token counter is rough on the edges.
    limit -= 500
    out = []
    for msg in reversed(history):
        if limit <= 0:
            break
        t = _count_tokens(msg['content'])
        limit -= t
        out.insert(0, msg)
    return out


def request(query, history):
    tokens = _openai_env['model_max_tokens'] - _openai_env['max_tokens']
    _history = history + [_msg("user", query)]
    h = _fit_history(_history, tokens)

    response = openai.ChatCompletion.create(
        messages=_system_context + h,
        temperature=_openai_env["temperature"],
        model=_openai_env["model"],
        max_tokens=_openai_env["max_tokens"],
        stream=True,
    )

    return rx.from_iterable(response).pipe(
        ops.map(lambda event: event['choices'][0]['delta'].get("content", '')),
        ops.filter(lambda x: x != "")
    )
