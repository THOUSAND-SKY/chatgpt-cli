import json
import os
import appdirs
import pathlib

from ai.history.abstract import AbstractCache
from ai.openai import fit_history

_context_var_name = "CHATGPT_CONTEXT"
_default_context_file = os.environ.get(_context_var_name, "default.json")


class FileCache(AbstractCache):
    def __init__(
        self,
        context=_default_context_file
    ) -> None:
        self._cache_dir = appdirs.user_cache_dir("chatgpt-cli")
        pathlib.Path(self._cache_dir).mkdir(exist_ok=True)
        self._context_file = pathlib.Path(
            self._cache_dir).joinpath(context)
        pathlib.Path(self._context_file).touch()

    def clear(self):
        pathlib.Path(self._context_file).unlink(missing_ok=True)

    def write(self, history):
        with open(self._context_file, "w") as f:
            json.dump(history, f, indent=2)

    def load(self):
        try:
            with open(self._context_file) as f:
                return json.load(f)
        except:
            return {}

    def print(self):
        with open(self._context_file) as f:
            history = json.load(f)
            if history:
                print("\n\n\n==================\n\n\n".join([item['content']
                      for item in fit_history(history["chat"])]))
            else:
                print("no history")


class TwoWayFileCache(AbstractCache):
    def __init__(self, load_file=_default_context_file, write_file=_default_context_file):
        self._from = FileCache(load_file)
        self._to = FileCache(write_file)

    def clear(self):
        self._to.clear()

    def write(self, history):
        self._to.write(history)

    def load(self):
        return self._from.load()

    def print(self):
        self._from.print()
