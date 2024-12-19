import os
from openai import OpenAI
import reactivex as rx
from reactivex import operators as ops
from anthropic import Anthropic
from anthropic.types import ContentBlockDeltaEvent, ContentBlockStartEvent
from groq import Groq

from ai.copilot import copilot_chat_completions


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

    if model.startswith("google-"):
        import google.generativeai as googlegenai
        googlegenai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        m = googlegenai.GenerativeModel(
            'models/' + model.removeprefix("google-"),
            system_instruction=system,
            generation_config=googlegenai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature))

        def transform_msg(message) -> googlegenai.types.content_types.ContentDict:
            role_map = {
                "user": "user",
                "assistant": "model",
            }
            return {"role": role_map[message["role"]], "parts": [message["content"]]}

        response = m.generate_content(
            [transform_msg(m) for m in messages],
            stream=True)
        return rx.from_iterable(response).pipe(
            ops.map(lambda event: ''.join(
                part.text for part in event.candidates[0].content.parts)),
        )

    if model.startswith("groq-"):
        g = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )
        response = g.chat.completions.create(
            messages=messages,
            model=model.removeprefix("groq-"),
            stream=True,
        )
        return rx.from_iterable(response).pipe(
            ops.map(lambda event: event.choices[0].delta.content or ""),
        )

    if model.startswith("copilot-"):
        response = copilot_chat_completions(
            os.environ.get("COPILOT_API_KEY") or "",
            [{"role": "system", "content": system}] + messages,
            temperature=temperature,
            model=model.removeprefix("copilot-")
        )
        return response

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
