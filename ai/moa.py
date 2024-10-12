"""
Mixture of Agents

https://github.com/togethercomputer/MoA
"""

import os
import reactivex as rx
from reactivex import operators as ops

from ai.models import send_message
from ai.util import fit_history
from ai.env import openai_env


_moa_env = {
    "models": os.environ.get("CHATGPT_CLI_MOA_MODELS", [
		"groq-llama3-70b-8192",
		"groq-mixtral-8x7b-32768",
		"groq-gemma-7b-it",
		"gpt-4o",
		"claude-3-5-sonnet-20240620"
	]),
}

def _msg(role, content):
    return {"role": role, "content": content}


def _make_system_prompt(responses: str):
    return f"""You have been provided with a set of responses from various open-source models to the latest user query. Your task is to synthesize these responses into a single, high-quality response. It is crucial to critically evaluate the information provided in these responses, recognizing that some of it may be biased or incorrect. Your response should not simply replicate the given answers but should offer a refined, accurate, and comprehensive yet brief reply to the instruction. Ensure your response is well-structured, coherent, and adheres to the highest standards of accuracy and reliability.

<responses>
""" + responses + """
</responses>"""

def request(query, history):
    _history = history + [_msg("user", query)]
    h = fit_history(_history, max_tokens=openai_env["max_tokens"], model_max_tokens=openai_env["model_max_tokens"])

    combiner_model = _moa_env["models"][-1]
    mix_models = _moa_env["models"][:-1]

    responses = rx.merge(*[send_message(
        system="Answer without preludes or greetings, keep your answer reasonably concise but do not omit important information. If you do not know the answer, just say you don't know.",
        messages=h,
        temperature=openai_env["temperature"],
        model=model,
        max_tokens=openai_env["max_tokens"],
    ).pipe(
        ops.to_list(),
        ops.map(lambda x: "".join(x)),
    ) for model in mix_models])

    return responses.pipe(
        ops.to_list(),
        ops.map(lambda x: "\n".join(
            f"""<response>
{x}
</response>"""
            for x in x
        )),
        # ops.do_action(lambda x: print(f"[MOA] {x}")),
        ops.flat_map_latest(
            lambda x: send_message(
                system=_make_system_prompt(x),
                messages=h,
                temperature=openai_env["temperature"],
                model=combiner_model,
                max_tokens=openai_env["max_tokens"],
            )
        )
    )
