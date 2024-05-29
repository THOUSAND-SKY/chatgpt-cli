import signal
from ai.history.abstract import AbstractCache
from ai.history.file_cache import FileCache
import ai.openai as openai
from reactivex import operators as ops
import argparse
import sys
import select
# Just importing this fixes arrow keys in `input`. Side effects ahoy!
# I think this is builtin?
import readline


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
        # exit(0)
    
    def write_and_exit(sig=None, frame=None):
        write()
        exit(0)

    signal.signal(signal.SIGINT, write_and_exit)

    def _concat(answer):
        nonlocal collected
        collected += answer

    ai_model.request(query, history.get("chat", [])).pipe(
        ops.do_action(lambda answer: print(answer, end='', flush=True)),
        ops.do_action(_concat)
    ).subscribe(
        on_completed=write
    )

def _get_stdin_data():
    # might only work on unix systems?
    if select.select([sys.stdin], [], [], 0.0)[0]:
    #     return sys.stdin.read()
    # if not sys.stdin.isatty():
        stdin_data = sys.stdin.read()
        return "\n\n" + stdin_data
    return ""

def _build_query(query: str, stdin_data: str):
    if stdin_data:
        return query + "\n\n" + stdin_data
    return query

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', default=False)
    # `-o` does nothing currently, since phind was removed.
    parser.add_argument('-o', '--openai', action='store_true', default=False)
    parser.add_argument('--print-history', action='store_true', default=False)
    parser.add_argument('-i', '--interactive', action='store_true', default=False)
    parser.add_argument('-q', '--quiet', action='store_true', default=False)
    parser.add_argument('args', nargs='*')
    args = parser.parse_args()

    history_manager = FileCache()
    if args.print_history:
        history_manager.print()
        return None

    query = " ".join(args.args) + _get_stdin_data()
    if args.clear or (not query and not args.interactive):
        history_manager.clear()
        if not args.quiet:
            print("Cleared history.", file=sys.stderr)
    if not query and not args.interactive:
        return None
    
    model = openai
    if args.interactive:
        ctrl_c_counter = 0
        while True:
            try:
                user_input = input(">>> ")
                if user_input.lower() == 'exit':
                    return
                respond(user_input, model, history_manager)
                ctrl_c_counter = 0
            except (EOFError, KeyboardInterrupt):
                ctrl_c_counter += 1
                if ctrl_c_counter == 2:
                    return
            except Exception as e:
                if not args.quiet:
                    print("An exception occurred:", str(e))
    respond(query, model, history_manager)


if __name__ == "__main__":
    main()
