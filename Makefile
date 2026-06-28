# Prefer a local .venv if present (local dev); otherwise use PATH (CI installs
# requirements.txt into the runner's python, so the tools are already on PATH).
# `!=` shell assignment works in both BSD make (saturn) and GNU make (CI).
BIN != if [ -x .venv/bin/zensical ]; then printf '.venv/bin/'; fi

PYTHON = $(BIN)python3
PLACEHOLDER = $(BIN)markdown-placeholder-standalone

# Zensical SSG
ZENSICAL = $(BIN)zensical
ZEN_CONFIG = zensical.toml
# Zensical opens many files via pygments; raise the fd limit to the host max.
# Soft->hard works locally and on CI runners. Never fail the recipe over it.
ZEN_ULIMIT = ulimit -n $$(ulimit -Hn) 2>/dev/null || true;

# In-repo zip-bundle browser assets (loaded directly under Zensical, no plugin).
ZIP_ASSETS = mkdocs_zip_bundle/assets

.PHONY: all build serve clean status help

all: build

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build    Build the static site with Zensical (+ placeholder post-process)"
	@echo "  serve    Build then serve the post-processed site at :8001"
	@echo "  clean    Remove build artifacts"
	@echo "  status   Show git status"

build:
	@echo "==> Building site with Zensical..."
	$(ZEN_ULIMIT) $(ZENSICAL) build -f $(ZEN_CONFIG)
	@echo "==> Copying in-repo zip-bundle assets into site/..."
	mkdir -p site/assets/zip-bundle
	cp $(ZIP_ASSETS)/* site/assets/zip-bundle/
	@echo "==> Injecting interactive placeholders (Zensical doesn't run the MkDocs plugin)..."
	@# --phase both: mark @VAR@ -> convert in ONE process (shared unique id).
	$(PLACEHOLDER) site/ --phase both --placeholder-config placeholder-plugin.yaml

# Serve the post-processed static output so placeholders work. NOT `zensical
# serve` — that rebuilds without the placeholder post-process (raw @VAR@) and
# without the copied zip-bundle assets.
serve: build
	@echo "==> Serving post-processed site/ at http://0.0.0.0:8001 (placeholders work; no live-reload)"
	$(PYTHON) -m http.server -d site --bind 0.0.0.0 8001

clean:
	@echo "==> Cleaning up..."
	rm -rf site/

status:
	git status
