import os
import openai
import reactivex as rx
from reactivex import operators as ops

# Set your OpenAI API key here
api_key = os.environ["OPENAI_API_KEY"]
openai.api_key = api_key


def _msg(role, content):
    return {"role": role, "content": content}


system_context = [_msg(
    "system", "You are ChatGPT, a large language model trained by OpenAI. You answer briefly and to the point.")]


def request(query, history):
    response = openai.ChatCompletion.create(
        messages=system_context + history + [_msg("user", query)],
        temperature=0.5,
        model="gpt-3.5-turbo",
        max_tokens=1500,
        stream=True,
    )

    return rx.from_iterable(response).pipe(
        ops.map(lambda event: event['choices'][0]['delta'].get("content", '')),
        ops.filter(lambda x: x != "")
    )
