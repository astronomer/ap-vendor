.DEFAULT_GOAL := help

.PHONY: help
help: ## Print Makefile help.
	@grep -Eh '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-28s\033[0m %s\n", $$1, $$2}'

.PHONY: install-hooks
install-hooks: ## Install git hooks
	command -v pre-commit || pip3 install --user --upgrade pre-commit
	pre-commit install -f --install-hooks

.PHONY: show-quay-urls
show-quay-urls: ## Show Quay.io URLS for all images in repo
	@find . -mindepth 1 -maxdepth 1 -type d -iname '[a-z]*' ! -name bin -print | sort | sed 's#^..#https://quay.io/astronomer/ap-#'

.PHONY: show-quay-pull-urls
show-quay-pull-urls: ## Show Quay.io pull for all images in repo
	@find . -mindepth 1 -maxdepth 1 -type d -iname '[a-z]*' ! -name bin -print | sort | while read -r dir ; do echo "quay.io/astronomer/ap-$${dir:2}:$$(cat $$dir/version.txt)" ; done ;

.PHONY: update-fluentd-gemfile.lock
update-fluentd-gemfile.lock: ## Update the fluentd Gemfile.lock file
	docker run -v "$$PWD/fluentd/include:/docker-share" --workdir=/docker-share --rm -ti ruby bundle update

