# Gradle-style task runner for the pythonbox monorepo.
MODULES := basic core files json math oo physics storage
MODULE_DIRS := $(addprefix modules/,$(MODULES))
SRC_DIRS := $(MODULE_DIRS:=/src)

.PHONY: install sync format lint typecheck clean help

help:
	@echo "pythonbox monorepo tasks (Gradle-style):"
	@echo "  make install    Install all modules editable (pip)"
	@echo "  make sync       Install all modules via uv workspace"
	@echo "  make format     Run black on all modules"
	@echo "  make lint       Run flake8 on all modules"
	@echo "  make typecheck  Run mypy on all modules"
	@echo "  make clean      Remove build artifacts"

install:
	@for m in $(MODULE_DIRS); do \
		echo "Installing $$m …"; \
		pip install -e "$$m"; \
	done

sync:
	uv sync --all-packages

format:
	black $(SRC_DIRS)

lint:
	flake8 $(SRC_DIRS) --max-line-length=88

typecheck:
	mypy $(SRC_DIRS) --ignore-missing-imports

clean:
	@find modules -type d -name '__pycache__' -prune -exec rm -rf {} +
	@find modules -type d -name '*.egg-info' -prune -exec rm -rf {} +
	@find modules -type d -name 'build' -prune -exec rm -rf {} +
