.PHONY: format black-check static-analysis type-check lint clean erlang

STATIC_ANALYSER_IMAGE := "docker.onedata.org/python_static_analyser:v8"
SRC_FILES := generators/

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
	$(call docker_run, isort $(SRC_FILES) --settings-file .pyproject.toml)
	$(call docker_run, black $(SRC_FILES) --config .pyproject.toml)

##
## Linting
##

black-check:
	$(call print_target)
	$(call docker_run, black $(SRC_FILES) --config .pyproject.toml --check) || (echo "Code failed Black format checking. Please run 'make format' before committing your changes."; exit 1)

static-analysis:
	$(call print_target)
	$(call docker_run, pylint $(SRC_FILES) --output-format=colorized --recursive=y --py-version=3.8 --rcfile=/tmp/rc_file)

type-check:
	$(call print_target)
	$(call docker_run, mypy $(SRC_FILES) --disable-error-code=import-untyped)

lint: black-check static-analysis type-check
	@:

##
## Generating
##

clean:
	@rm -rf generated
	@echo "Cleaned generated files."

erlang:
	python -m generators.erlang.gen_erl
