# To use this script, you ought to bind it to a key, e.g.
#
# $ bind \cq __chatgpt_shell_integration
#
# Then hit ctrl+q after typing out your prompt on the cli.
# You will also need the `chatgpt.fish` script.
#
function __chatgpt_shell_integration
    set current (commandline)
    set -l prompt_length (string length "$current")
    set current (string replace "[^\\]'" "'\\''" -- $current)
    set current (string replace "[^\\]|" "\\|" -- $current)
    for i in (seq $prompt_length)
        echo -n (tput cub1)
    end
    set out ""
    set cwd (pwd | string replace '/' '' --all)
    stdbuf -o0 fish -c "CHATGPT_CLI_OPENAI_MODEL_MAX_TOKENS=500 CHATGPT_CLI_OPENAI_SYSTEM_PROMPT='You answer with only a unix commandline command, in plain text, no markdown. User is using Fish shell, but avoid builtins so scripts work in bash as well.' CHATGPT_CONTEXT='shell-$cwd' chatgpt -q -- '$current'" | while read -l -n1 line
        echo -n "$line"
        set out "$out$line"
    end

    commandline -f force-repaint

    commandline -r "$out"

    commandline -f force-repaint
end
