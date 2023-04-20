.DEFAULT_GOAL := help

image_name:=
image_tag:=latest
image_test_config:=$(image_name)/test.yaml

.PHONY: help
help: ## Print Makefile help.
	@grep -Eh '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-28s\033[0m %s\n", $$1, $$2}'

.PHONY: install-hooks
install-hooks: ## Install git hooks
	command -v pre-commit || pip3 install --user --upgrade pre-commit
	pre-commit install -f --install-hooks

.PHONY: show-quay-urls
show-quay-urls: ## Show Quay.io URLS for all images in repo
	@find . -mindepth 1 -maxdepth 1 -type d -iname '[a-z]*' ! -name bin ! -name requirements -print | sort | sed 's#^\./\(.*\)#https://quay.io/repository/astronomer/ap-\1?tab=tags#'

.PHONY: show-quay-pull-urls
show-quay-pull-urls: ## Show Quay.io pull for all images in repo
	@find . -mindepth 1 -maxdepth 1 -type d -iname '[a-z]*' ! -name bin ! -name requirements -print | sort | while read -r dir ; do echo "quay.io/astronomer/ap-$${dir:2}:$$(cat $$dir/version.txt)" ; done ;

.PHONY: update-fluentd-gemfile.lock
update-fluentd-gemfile.lock: ## Update the fluentd Gemfile.lock file
	docker run -v "$$PWD/fluentd/include:/docker-share" --workdir=/docker-share --rm -ti ruby bundle update

.PHONY: update-requirements
update-requirements: ## Update all requirements.txt files
	for FILE in requirements/*.in ; do pip-compile --quiet --generate-hashes --allow-unsafe --upgrade $${FILE} ; done ;
	-pre-commit run requirements-txt-fixer --all-files --show-diff-on-failure

.PHONY: build
build: ## Build the docker image with docker-compose. Ex: `make build image_name=alertmanager`
	docker-compose build ap-$(image_name)

.PHONY: test
test: export ASTRO_IMAGE_NAME = ap-$(image_name)
test: export ASTRO_IMAGE_TAG = $(image_tag)
test: export ASTRO_IMAGE_TEST_CONFIG_PATH = $(image_test_config)

test: ## Test the docker image. Ex: `make test image_name=alertmanager`
	env | grep ASTRO
	pytest -v -s bin/test.py
