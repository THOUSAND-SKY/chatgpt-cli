import os


openai_env = {
    "model_max_tokens": int(os.environ.get("CHATGPT_CLI_OPENAI_MODEL_MAX_TOKENS", "4000")),
    "max_tokens": int(os.environ.get("CHATGPT_CLI_OPENAI_RESPONSE_MAX_TOKENS", "1000")),
    "model": os.environ.get("CHATGPT_CLI_OPENAI_MODEL", "gpt-3.5-turbo"),
    "temperature": float(os.environ.get("CHATGPT_CLI_OPENAI_TEMPERATURE", "0")),
    "system_prompt": os.environ.get("CHATGPT_CLI_OPENAI_SYSTEM_PROMPT", "You answer briefly and to the point.")
}

