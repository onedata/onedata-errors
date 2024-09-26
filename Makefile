.PHONY: submodules venv init format black-check static-analysis type-check lint test-with-clean test-without-clean dist pypi_check pypi_upload

STATIC_ANALYSER_IMAGE := "docker.onedata.org/python_static_analyser:v7"
ERLANG_GENERATOR := generators/erlang/gen_erl.py
SRC_FILES := $(ERLANG_GENERATOR)

UID := $(shell id -u)
GID := $(shell id -g)

define docker_run
	docker run --rm -i -v $(CURDIR):$(CURDIR) -w $(CURDIR) -u $(UID):$(GID) $(STATIC_ANALYSER_IMAGE) $1
endef

bold := $(shell tput bold)
normal := $(shell tput sgr0)
blue := $(shell tput setaf 4)

# Function to print target name
define print_target
	@echo ""
	@echo "$(blue)$(bold)$@:$(normal)"
endef

##
## Formatting
##

format:
	$(call print_target)
	$(call docker_run, isort -rc $(SRC_FILES))
	$(call docker_run, black --fast $(SRC_FILES))

##
## Linting
##

black-check:
	$(call print_target)
	$(call docker_run, black $(SRC_FILES) --check) || (echo "Code failed Black format checking. Please run 'make format' before commiting your changes."; exit 1)

static-analysis:
	$(call print_target)
	$(call docker_run, pylint $(SRC_FILES) --rcfile=.pylintrc --recursive=y)

type-check:
	$(call print_target)
	$(call docker_run, mypy $(SRC_FILES) --ignore-missing-imports)

lint: black-check static-analysis type-check
	@:

##
## Generating
##

clean:
	@rm -rf generated

erlang:
	python $(ERLANG_GENERATOR)
