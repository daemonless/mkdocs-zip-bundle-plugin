PYTHON = python3
MKDOCS = NO_MKDOCS_2_WARNING=1 mkdocs

.PHONY: all build serve clean status help

all: build

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build    Build the static site using mkdocs"
	@echo "  serve    Run local mkdocs development server"
	@echo "  clean    Remove build artifacts"
	@echo "  status   Show git status"

build:
	@echo "==> Building site with mkdocs..."
	$(MKDOCS) build

serve:
	$(MKDOCS) serve -a 0.0.0.0:8888

clean:
	@echo "==> Cleaning up..."
	rm -rf site/

status:
	git status
