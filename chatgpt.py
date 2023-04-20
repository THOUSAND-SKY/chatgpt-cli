import signal
from ai.history.abstract import AbstractCache
from ai.history.file_cache import FileCache
import ai.openai as openai
import ai.phind as phind
from reactivex import operators as ops
import argparse


def respond(query, ai_model, history_manager: AbstractCache):
    history = history_manager.load()

    collected = ''

    def write(sig=None, frame=None):
        user_query = [{"role": "user", "content": query}]
        assistant_response = [
            {"role": "assistant", "content": collected.strip()}]
        history["chat"] = history.get(
            "chat", []) + user_query + assistant_response

        history_manager.write(history)
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', default=False)
    # take optional boolean flag -o for openai or -p for phind, and any number of arguments as input
    parser.add_argument('-o', '--openai', action='store_true', default=False)
    parser.add_argument('-p', '--phind', action='store_true', default=False)
    parser.add_argument('--print-history', action='store_true', default=False)
    parser.add_argument('args', nargs='*')
    args = parser.parse_args()
    model = openai if args.openai else phind

    history_manager = FileCache()
    # needs to be before
    if args.print_history:
        history_manager.print()
        return None

    query = " ".join(args.args)
    if args.clear or not query:
        history_manager.clear()
        print("Cleared history.")
    if not query:
        return None

    respond(query, model, history_manager)


if __name__ == "__main__":
    main()
