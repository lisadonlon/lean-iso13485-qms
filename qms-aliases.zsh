# QMS — shell aliases
#
# Source this from ~/.zshrc with:
#   [ -f "/path/to/qms/qms-aliases.zsh" ] && source "/path/to/qms/qms-aliases.zsh"
#
# It self-locates the vault (the directory this file lives in). To point it
# elsewhere, set QMS_VAULT before sourcing.

# Self-locate: ${(%):-%x} is the path of the file currently being sourced (zsh).
export QMS_VAULT="${QMS_VAULT:-${${(%):-%x}:A:h}}"

# qms-make wraps `make` so commands run against the vault from any cwd,
# without changing the user's pwd. The subshell isolates the cd.
qms-make() {
    (cd "$QMS_VAULT" && make "$@")
}

# Jump to the vault interactively (this DOES change pwd, on purpose).
alias qms="cd \"$QMS_VAULT\""

# Validation
alias qms-validate='qms-make validate'
alias qms-validate-dry='qms-make validate-dry'

# Audit export
alias qms-export='qms-make export'
alias qms-export-test='qms-make export-test'

# Git / status
alias qms-status='qms-make status'
alias qms-log='qms-make log'
alias qms-tags='qms-make tags'
alias qms-push='qms-make push'
alias qms-approved='qms-make approved'
alias qms-dirty-check='qms-make dirty-check'

# Help
alias qms-help='qms-make help'
