import json
import openai
import os
import sys
import pathlib
import signal
import appdirs

# Set your OpenAI API key here
api_key = os.environ["OPENAI_API_KEY"]
openai.api_key = api_key

cache_dir = appdirs.user_cache_dir("chatgpt-cli")
pathlib.Path(cache_dir).mkdir(exist_ok=True)


def chatgpt(query):
    context_var_name = "CHATGPT_CONTEXT"
    context_file = pathlib.Path(cache_dir).joinpath(
        os.environ.get(context_var_name, "default.json"))

    if not query:
        print("Cleared history.")
        pathlib.Path(context_file).unlink()
        return None

    pathlib.Path(context_file).touch()

    with open(context_file, "r+") as f:
        system_context = [
            {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. You answer briefly and to the point."},
        ]
        try:
            history = json.load(f)
        except:
            history = {}
        user_query = [{"role": "user", "content": query}]

        response = openai.ChatCompletion.create(
            messages=system_context + history.get("chat", []) + user_query,
            temperature=0.5,
            model="gpt-3.5-turbo",
            max_tokens=1500,
            stream=True,
        )

        history["chat"] = history.get("chat", []) + user_query

        answer = ''
        collected = ''

        def write(sig=None, frame=None):
            history["chat"] = history.get(
                "chat", []) + [{"role": "assistant", "content": collected.strip()}]

            f.seek(0)
            json.dump(history, f)
            f.truncate()
            exit(0)

        signal.signal(signal.SIGINT, write)

        for event in response:
            # STREAM THE ANSWER
            # Print the response
            print(answer, end='', flush=True)
            # RETRIEVE THE TEXT FROM THE RESPONSE
            event_text = event['choices'][0]['delta']  # EVENT DELTA RESPONSE
            answer = event_text.get('content', '')  # RETRIEVE CONTENT
            collected += f" {answer}"
        print()
        write()


# Get the query from command-line argument
if __name__ == "__main__":
    query = " ".join(sys.argv[1:])
    chatgpt(query)
