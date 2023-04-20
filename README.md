# ChatGPT CLI

ChatGPT CLI. Streaming text. Has memory.

Now uses [phind.com](https://phind.com) by default. Two choices: phind or openai.

Phind specializes in programming.

## Installation

1. Clone the repository

2. Install the required dependencies

   ```sh
   $ python3 -m pip install -r requirements.txt --user
   ```

3. If using openai, set your OpenAI API key. E.g. `export OPENAI_API_KEY="123"`.

   You can obtain your API key from the [OpenAI website](https://platform.openai.com/account/api-keys).

   Phind is free. No API key.

## Usage

You can run the ChatGPT CLI by executing the Python script with a query as an argument. For example:

```sh
$ # The included 'chatgpt' script will do per-directory chat history.
$ # using phind
$ chatgpt hi what is up # ...or
$ chatgpt "hi what's up"

$ chatgpt -o hi what is up # openai chatgpt (api key required)

$ chatgpt -c 'the `-c` first clears history, then sends this as usual (without history).'
```

The query will be used as a user message in the conversation with the model. The program will stream the response from the model and display it on the terminal.

You can also clear the conversation history by passing an empty query:

```sh
$ chatgpt # Clears history
```

## How it works

It sends a series of messages as input to the API, including system messages, user messages, and assistant messages. The assistant message contains the response from the model.

The conversation history is stored in a JSON file in the cache directory, which can be customized using the `XDG_CACHE_DIR` (usually `~/.cache`) environment variable. The program streams the response from the model and displays it on the terminal. It also handles interrupts (SIGINT) to save the conversation history before exiting.

## Contributing

If you encounter any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request on the GitHub repository: https://github.com/your_username/your_repository

## License

This program is released under the MIT License. See the [LICENSE](https://github.com/your_username/your_repository/blob/main/LICENSE) file for more details.

> This readme was written by chatgpt
