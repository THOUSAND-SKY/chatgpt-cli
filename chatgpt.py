import json
import os
import pathlib
import signal
import appdirs
import ai.openai as openai
import ai.phind as phind
from reactivex import operators as ops
import argparse

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

        collected = ''

        def write(sig=None, frame=None):
            user_query = [{"role": "user", "content": query}]
            assistant_ressponse = [
                {"role": "assistant", "content": collected.strip()}]
            history["chat"] = history.get(
                "chat", []) + user_query + assistant_ressponse

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
    parser = argparse.ArgumentParser()
    # take optional boolean flag -o for openai or -p for phind, and any number of arguments as input
    parser.add_argument('-o', '--openai', action='store_true', default=False)
    parser.add_argument('-p', '--phind', action='store_true', default=False)
    parser.add_argument('args', nargs='*')
    args = parser.parse_args()
    model = openai if args.openai else phind

    respond(" ".join(args.args), model)
