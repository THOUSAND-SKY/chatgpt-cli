import reactivex as rx
from reactivex import operators as ops
import requests
from datetime import datetime
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:112.0) Gecko/20100101 Firefox/112.0',
    'Content-Type': 'application/json',
}


def _url(history):
    if len(history) == 0:
        return 'https://www.phind.com/api/infer/followup/answer'
    return 'https://www.phind.com/api/infer/answer'


def _date_now():
    return datetime.today().strftime("%-m/%-d/%Y")


def _msg(query, answers, questions):
    return {
        "question": query,
        "questionHistory": questions,
        "answerHistory": answers,
        "userRankList": {},
        "browserLanguage": "en-US",
        "options": {
            "creative": False,
            "date": _date_now(),
            "detailed": False,
            "language": "en-US",
            "skill": "expert"
        }
    }


def request(query, history):
    answers = [item['content']
               for item in history if item["role"] == "assistant"]
    questions = [item['content'] for item in history if item["role"] == "user"]
    body = _msg(query, answers, questions)
    response = requests.post(_url(history), json=body,
                             headers=headers, stream=True)

    return rx.from_iterable(response.iter_lines(decode_unicode=True)).pipe(
        ops.filter(lambda r: r != ""),
        ops.map(lambda r: re.sub(r"data: ?", "", r)),
        ops.map(lambda r: "\n" if r == "" else r),
    )
