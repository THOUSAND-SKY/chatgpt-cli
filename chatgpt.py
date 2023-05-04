import signal
from ai.history.abstract import AbstractCache
from ai.history.file_cache import FileCache
import ai.openai as openai
from reactivex import operators as ops
import argparse
import sys


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
        collected += answer

    ai_model.request(query, history.get("chat", [])).pipe(
        ops.do_action(lambda answer: print(answer, end='', flush=True)),
        ops.do_action(_concat)
    ).subscribe(
        on_completed=write
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', default=False)
    # `-o` does nothing currently, since phind was removed.
    parser.add_argument('-o', '--openai', action='store_true', default=False)
    parser.add_argument('--print-history', action='store_true', default=False)
    parser.add_argument('args', nargs='*')
    args = parser.parse_args()

    history_manager = FileCache()
    if args.print_history:
        history_manager.print()
        return None

    query = " ".join(args.args)
    if args.clear or not query:
        history_manager.clear()
        print("Cleared history.", file=sys.stderr)
    if not query:
        return None

    model = openai
    respond(query, model, history_manager)


if __name__ == "__main__":
    main()
