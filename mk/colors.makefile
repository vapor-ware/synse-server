# ------------------------------------------------------------------------
#  Author: Thomas Rampelberg (thomasr@vapor.io)
#  Dependencies:
#  Description: Provide functions to print messages with color.
# ------------------------------------------------------------------------

export NO_COLOR=\033[0m
export OK_COLOR=\033[32;01m
export ERROR_COLOR=\033[31;01m
WARN_COLOR=\033[33;01m

OK_STRING=$(OK_COLOR)[OK]$(NO_COLOR)
ERROR_STRING=$(ERROR_COLOR)[ERROR]$(NO_COLOR)
WARN_STRING=$(WARN_COLOR)[WARN]$(NO_COLOR)

AWK_CMD = awk '{ printf "%-30s %-10s\n",$$1, $$2; }'
export PRINT_OK = printf "$@ $(OK_STRING)\n" | $(AWK_CMD)

# Output an error to the console, including the target that experienced the error.
define print_error
	printf "$@ $(ERROR_STRING)\n" | $(AWK_CMD) \
		&& printf "    " \
		&& printf $(1) \
		&& printf "\n\n" \
		&& false
endef
