import os
from typing import Dict, List
from openai import OpenAI
import reactivex as rx
from reactivex import operators as ops

from anthropic import Anthropic
from anthropic.types import ContentBlockDeltaEvent, ContentBlockStartEvent


def send_message(
    system: str,
    model: str,
    max_tokens: int,
    temperature: int,
    messages,  # [{content, role}]
):
    if model.startswith("claude"):
        a = Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )
        response = a.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[
                {
                    "role": msg["role"],
                    "content": [{"type": "text", "text": msg["content"]}],
                }
                for msg in messages
            ],
            stream=True,
        )
        return rx.from_iterable(response).pipe(
            ops.map(
                lambda event: (
                    event.content_block.text
                    if isinstance(event, ContentBlockStartEvent)
                    else (
                        event.delta.text
                        if isinstance(event, ContentBlockDeltaEvent)
                        else ""
                    )
                )
            ),
        )

    response = OpenAI(api_key=os.environ.get("OPENAI_API_KEY")).chat.completions.create(
        messages=[{"role": "system", "content": system}] + messages,
        temperature=temperature,
        model=model,
        max_tokens=max_tokens,
        stream=True,
    )
    return rx.from_iterable(response).pipe(
        ops.map(lambda event: event.choices[0].delta.content or ""),
    )
