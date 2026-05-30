# Configuration

## Plugin options

```yaml
plugins:
  - zip-bundle:
      include_jszip: true        # Bundle JSZip — set false if you load it yourself
      zip_label_suffix: "(.zip)" # Suffix appended to multi-file bundle button labels
```

| Option | Default | Description |
|--------|---------|-------------|
| `include_jszip` | `true` | Inject the bundled JSZip library. Set to `false` if you already load JSZip via `extra_javascript`. |
| `zip_label_suffix` | `"(.zip)"` | Text appended to the auto-generated label for multi-file bundles. |

## Code block attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `data-zip-bundle` | Yes | Bundle ID. Blocks with the same ID are grouped into one download. |
| `data-zip-filename` | Yes | Filename inside the ZIP (or the downloaded filename for single files). Supports paths: `config/app.yaml`. |
| `data-zip-label` | No | Override the auto-generated button label. |
| `data-zip-force` | No | Set to `"true"` to always produce a ZIP even for a single file. |

## Required markdown extensions

```yaml
markdown_extensions:
  - attr_list          # Required — reads data-zip-* attributes on code blocks
  - pymdownx.superfences  # Recommended for reliable fenced code block attribute support
```

## Using with Zensical

[Zensical](https://zensical.org) isn't built on MkDocs and doesn't run MkDocs
plugins, so there's no `plugins:` entry. Instead, load the three browser assets
via `extra_javascript` / `extra_css` — the button injection and ZIP/download
logic all run client-side, so the behavior is identical.

```yaml
extra_javascript:
  - https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js
  - https://cdn.jsdelivr.net/gh/daemonless/mkdocs-zip-bundle-plugin@v0.2.0/mkdocs_zip_bundle/assets/zip-bundle.js
extra_css:
  - https://cdn.jsdelivr.net/gh/daemonless/mkdocs-zip-bundle-plugin@v0.2.0/mkdocs_zip_bundle/assets/zip-bundle.css
```

> The `@v0.2.0` pins to the release tag — bump it to match the version you want.

The [markdown extensions](#required-markdown-extensions) and
[code block attributes](#code-block-attributes) are exactly the same as the
MkDocs setup. You don't install the Python package at all for Zensical — only
the assets are needed.

**Offline / air-gapped builds:** instead of the CDN URLs, copy the three files
(`jszip.min.js`, `zip-bundle.js`, `zip-bundle.css`) from the package's
`mkdocs_zip_bundle/assets/` directory into your project and reference them by
local path.

> **Placeholder integration is not (yet) confirmed on Zensical.** The
> [live-values](#placeholder-integration) feature relies on
> [`mkdocs-placeholder-plugin`](https://github.com/six-two/mkdocs-placeholder-plugin),
> whose placeholder *wrapping* runs at MkDocs build time and does not run under
> Zensical. Its author has decoupled the runtime and ships a standalone script,
> but a Zensical-compatible setup isn't documented or verified. On Zensical,
> zip-bundle downloads the code blocks **as written** — the ZIP/download itself
> works fully; only the live-value substitution depends on placeholder support.

## Placeholder integration

Pair with [`mkdocs-placeholder-plugin`](https://github.com/six-two/mkdocs-placeholder-plugin) so downloaded files contain the user's live edited values instead of defaults:

```yaml
plugins:
  - search
  - zip-bundle
  - placeholder:
      placeholder_file: placeholder-plugin.yaml
```

The download button captures the **current rendered text** of the code block at click time — whatever the user has typed into the placeholder inputs is what ends up in the file.
