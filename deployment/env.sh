_ANSIBLE_VAULT_OPT="--vault-password-file $HOME/.ansible_pass"
_ANSIBLE_HOSTFILE="hosts"
SERVER_IP=$(cat $_ANSIBLE_HOSTFILE |head -n2 |tail -n1 |cut -d' ' -f1)

alias playbook="ansible-playbook $_ANSIBLE_VAULT_OPT -i $_ANSIBLE_HOSTFILE"
alias vault="ansible-vault $_ANSIBLE_VAULT_OPT edit"
alias ansible="ansible $_ANSIBLE_VAULT_OPT -i $_ANSIBLE_HOSTFILE rufian"
alias shell="ssh root@$SERVER_IP"
alias site="playbook site.yml"
alias tag="site --tags"
alias tags="tag"
alias sslup="./sslman.py -u && tag ssl"

function mkrole() {
  set -eu
  mkdir -p roles/$1/{files,handlers,tasks,templates}
  touch roles/$1/tasks/main.yml
  touch roles/$1/handlers/main.yml
}
