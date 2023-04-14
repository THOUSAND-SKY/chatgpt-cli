import json
import os
import sys
import pathlib
import signal
import appdirs
import ai.openai as openai
import ai.phind as phind
from reactivex import operators as ops

cache_dir = appdirs.user_cache_dir("chatgpt-cli")
pathlib.Path(cache_dir).mkdir(exist_ok=True)


def respond(query, ai_model):
    context_var_name = "CHATGPT_CONTEXT"
    context_file = pathlib.Path(cache_dir).joinpath(
        os.environ.get(context_var_name, "default.json"))

    if not query:
        print("Cleared history.")
        pathlib.Path(context_file).unlink(missing_ok=True)
        return None

    pathlib.Path(context_file).touch()

    with open(context_file, "r+") as f:
        try:
            history = json.load(f)
        except:
            history = {}
        user_query = [{"role": "user", "content": query}]

        history["chat"] = history.get("chat", []) + user_query

        collected = ''

        def write(sig=None, frame=None):
            history["chat"] = history.get(
                "chat", []) + [{"role": "assistant", "content": collected.strip()}]

            f.seek(0)
            json.dump(history, f)
            f.truncate()
            print()
            exit(0)

        signal.signal(signal.SIGINT, write)

        def _concat(answer):
            nonlocal collected
            collected += f" {answer}"

        ai_model.request(query, history.get("chat", [])).pipe(
            ops.do_action(lambda answer: print(answer, end='', flush=True)),
            ops.do_action(_concat)
        ).subscribe(
            on_completed=write
        )


# Get the query from command-line argument
if __name__ == "__main__":
    query = " ".join(sys.argv[1:])
    # Swap the commented and uncommented lines if need be.
    # respond(query, openai)
    respond(query, phind)
