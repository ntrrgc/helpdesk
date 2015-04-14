alias s='sudo'
alias pas='sudo yum -y install'
alias yas='sudo yum -y install'
alias pass='sudo yum search'
alias yass='sudo yum search'
alias pai='rpm -qi'
alias par='sudo yum autoremove'
alias l='ls'
alias ll='ls -lh'
function cmkdir() {
    mkdir "$1" && cd "$1"
}
shopt -s autocd
shopt -s histappend

COLOR_RESET="\[\e[m\]"
COLOR_RESET_NO_PS="\e[m"
COLOR_GREEN="\[\e[38;5;$((24+88))m\]"
COLOR_YELLOW="\[\e[38;5;$((196+32))m\]"
COLOR_BLUE="\[\e[38;5;$((22+52))m\]"
COLOR_RED="\[\e[38;5;$((196+7))m\]"
COLOR_RED_NO_PS="\e[38;5;$((196+7))m"
COLOR_ORANGE="\[\e[38;5;$((196+12))m\]"
COLOR_CYAN="\[\e[38;5;$((29+124))m\]"

PS_TIME="${COLOR_GREEN}[\$(date +%k:%M:%S)]${COLOR_RESET}"
PS_PWD="${COLOR_BLUE}\w${COLOR_RESET}"
PS_USER="${COLOR_YELLOW}\u@\h${COLOR_RESET}"
PS_STAR="${COLOR_ORANGE}$(echo -ne '\xe2\x9b\xa4')${COLOR_RESET}"
PS_SNOW="${COLOR_CYAN}$(echo -ne '\xe2\x9d\x85')${COLOR_RESET}"

PS_FIRST_TIME=true
function __prompt_command() {
  local ret=$?
  if $PS_FIRST_TIME; then
    PS_FIRST_TIME=false
  else
    # Show return code of previous command
    if [[ $ret != 0 ]]; then
      echo -e "${COLOR_RED_NO_PS}exited with code $ret ✘ ${COLOR_RESET_NO_PS}"
    fi

    # Print always a newline except if it's the first line
    echo
  fi
}
PROMPT_COMMAND='__prompt_command'

PS1="${PS_TIME} ${PS_PWD}
${PS_USER}${COLOR_BLUE}❯ ${COLOR_RESET}"
