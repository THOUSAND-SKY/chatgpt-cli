# ChatGPT CLI

ChatGPT CLI. Streaming text. Has memory.

![Example](scripts/assets/screencast.webp).

> Here's an alternative with a bunch of features: https://github.com/TheR1D/shell_gpt

## Installation

1. Clone the repository

2. Install the required dependencies

   ```sh
   $ python3 -m pip install . --user
   ```

3. If using openai, set your OpenAI API key. E.g. `export OPENAI_API_KEY="123"`.

   You can obtain your API key from the [OpenAI website](https://platform.openai.com/account/api-keys).

4. Optionally, symlink the provided `chatgpt` script to your path.

   ```sh
   $ ln -s "$PWD/chatgpt" "$HOME/bin" # assuming ~/bin is in PATH
   ```

## Usage

You can run the ChatGPT CLI by executing the Python script with a query as an argument. For example:

```sh
$ # The included 'chatgpt' script will do per-directory chat history.
$ chatgpt hi what is up # ...or
$ chatgpt "hi what's up"

$ chatgpt -c 'the `-c` first clears history, then sends this as usual (without history).'
```

The query will be used as a user message in the conversation with the model. The program will stream the response from the model and display it on the terminal.

You can also clear the conversation history by passing an empty query:

```sh
$ chatgpt # Clears history
```

[ai/openai.py](ai/openai.py) contains env variables for request customization, e.g. model name.

### Models

#### Anthropic <anthropic.com>

`CHATGPT_CLI_OPENAI_MODEL=claude-3-5-sonnet-20241022` + `ANTHROPIC_API_KEY`

#### Google <aistudio.google.com>

Prefix with `google-`.

`CHATGPT_CLI_OPENAI_MODEL=google-gemini-2.0-flash-exp` + `GOOGLE_API_KEY`

#### OpenAI <openai.com>

`CHATGPT_CLI_OPENAI_MODEL=gpt-4o` + `OPENAI_API_KEY`

#### Groq <groq.com>

Prefix with `groq-`.

`CHATGPT_CLI_OPENAI_MODEL=groq-llama3.2-3b-preview` + `GROQ_API_KEY`

#### Github copilot

> I had gh copilot for 30days for the trial, I don't anymore so I don't know if this model will work anymore.

Prefix with `copilot-`.

`CHATGPT_CLI_OPENAI_MODEL=copilot-gpt4o` (Dunno what the model is now, used to be gpt4.)

## How it works

It sends a series of messages as input to the API, including system messages, user messages, and assistant messages. The assistant message contains the response from the model.

The conversation history is stored in a JSON file in the cache directory, which can be customized using the `XDG_CACHE_DIR` (usually `~/.cache`) environment variable. The program streams the response from the model and displays it on the terminal. It also handles interrupts (SIGINT) to save the conversation history before exiting.

## Contributing

If you encounter any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request on the GitHub repository: https://github.com/your_username/your_repository

### Known bugs

- Don't know if works on Windows.

#### `__chatgpt_shell_integration.fish`

- Some prompts fail at escaping and crash
- Running in a shell with an altered env sometimes fails for reasons
  such as modified LD_PRELOAD (or some other c/c++ junk?)
  e.g. in a `nix shell`.
- Prompts for shell command querying (e.g. ctrl-q in shell) don't save in shell history

#### Cli

The interactive mode responses can't be cut off with ctrl-c.

## License

This program is released under the MIT License. See the [LICENSE](https://github.com/your_username/your_repository/blob/main/LICENSE) file for more details.

> This readme was written by chatgpt
