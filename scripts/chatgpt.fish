# This is an example script for fish shell.
function chatgpt
    argparse --ignore-unknown '3/gpt3' -- $argv || return

	set script_path (status --current-filename)
	set script_dir (dirname $script_path)

    if test -z "$CHATGPT_CONTEXT"
         set CHATGPT_CONTEXT (pwd | string replace --all "/" "")
    end

    # I use secret-tool for getting the key here.
    set key (secret-tool lookup apikeys/openai something)
    if test -n "$_flag_gpt3"
        echo "Using GPT3.5."
        CHATGPT_CLI_OPENAI_MODEL="gpt-3.5-turbo" OPENAI_API_KEY=$key python3 CHATGPT_CONTEXT="$CHATGPT_CONTEXT" "$script_dir/chatgpt.py" $argv
        return
    end
    CHATGPT_CLI_OPENAI_MODEL="gpt-4-turbo-preview" CHATGPT_CLI_OPENAI_MODEL_MAX_TOKENS="800" CHATGPT_CLI_OPENAI_RESPONSE_MAX_TOKENS="500" CHATGPT_CONTEXT="$CHATGPT_CONTEXT" OPENAI_API_KEY=$key python3 "$script_dir/chatgpt.py" $argv
end
