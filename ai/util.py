from itertools import dropwhile
from math import ceil


def safe_get_element_by_index(lst, index):
    if index < 0 or index >= len(lst):
        return None
    return lst[index]

def fit_history(history, max_tokens, model_max_tokens):
    limit = model_max_tokens - max_tokens

    def _count_tokens(str):
        return max(ceil(len(str) / 4), 1)

    # Extra leeway because token counter is rough on the edges.
    limit -= limit * 0.2
    out = []
    for msg in reversed(history):
        if limit <= 0:
            break
        t = _count_tokens(msg["content"])
        limit -= t
        out.insert(0, msg)
    return list(dropwhile(lambda t: t['role'] != 'user', out))
