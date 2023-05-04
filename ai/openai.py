import os
import openai
import reactivex as rx
from reactivex import operators as ops

# Set your OpenAI API key here
openai.api_key = os.environ.get("OPENAI_API_KEY")

_openai_env = {
    "max_tokens": int(os.environ.get("CHATGPT_CLI_OPENAI_MAX_TOKENS", "1000")),
    "model": os.environ.get("CHATGPT_CLI_OPENAI_MODEL", "gpt-3.5-turbo"),
    "temperature": float(os.environ.get("CHATGPT_CLI_OPENAI_TEMPERATURE", "0.5")),
    "system_prompt": os.environ.get("CHATGPT_CLI_OPENAI_SYSTEM_PROMPT", "You are ChatGPT, a large language model trained by OpenAI. You answer briefly and to the point.")
}


def _msg(role, content):
    return {"role": role, "content": content}


_system_context = [_msg(
    "system", _openai_env["system_prompt"])]


def request(query, history):
    response = openai.ChatCompletion.create(
        messages=_system_context + history + [_msg("user", query)],
        temperature=_openai_env["temperature"],
        model=_openai_env["model"],
        max_tokens=_openai_env["max_tokens"],
        stream=True,
    )

    return rx.from_iterable(response).pipe(
        ops.map(lambda event: event['choices'][0]['delta'].get("content", '')),
        ops.filter(lambda x: x != "")
    )
