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

[Zensical](https://zensical.org) doesn't run MkDocs plugins, so there's no
`plugins:` entry — you don't install the Python package at all. Instead, load
the browser assets directly; the button injection and ZIP/download logic all run
client-side, so the behavior is identical.

In Zensical's native [`zensical.toml`](https://zensical.org/compatibility/configuration/)
everything lives under a `[project]` scope:

```toml
# zensical.toml
[project]
extra_css = [
  "https://cdn.jsdelivr.net/gh/daemonless/mkdocs-zip-bundle-plugin@v0.2.0/mkdocs_zip_bundle/assets/zip-bundle.css",
]
extra_javascript = [
  "https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js",
  "https://cdn.jsdelivr.net/gh/daemonless/mkdocs-zip-bundle-plugin@v0.2.0/mkdocs_zip_bundle/assets/zip-bundle.js",
]

# attr_list is required so Zensical reads the data-zip-* attributes
[project.markdown_extensions.attr_list]
[project.markdown_extensions.pymdownx.superfences]
```

> The `@v0.2.0` pins to the release tag — bump it to match the version you want.

If you're migrating an existing project, Zensical also reads your current
`mkdocs.yml` unchanged through its compatibility layer, so the
`extra_javascript` / `extra_css` and `markdown_extensions` from the
[MkDocs setup](#required-markdown-extensions) work as-is — just drop the
`plugins: - zip-bundle` entry, since the plugin doesn't run under Zensical.

The [code block attributes](#code-block-attributes) are identical to the MkDocs
setup.

**Offline / air-gapped builds:** instead of the CDN URLs, copy the three files
(`jszip.min.js`, `zip-bundle.js`, `zip-bundle.css`) from the package's
`mkdocs_zip_bundle/assets/` directory into your project and reference them by
local path.

### Placeholder live-values on Zensical

The [live-values](#placeholder-integration) feature works on Zensical, but it
needs **one post-build step**. The `@VAR@` *wrapping* normally done by
[`mkdocs-placeholder-plugin`](https://github.com/six-two/mkdocs-placeholder-plugin)
at MkDocs build time doesn't run under Zensical, so post-process the built site
with the plugin's standalone CLI (shipped in `mkdocs-placeholder-plugin>=0.7.0`):

```bash
zensical build
markdown-placeholder-standalone site/ --phase both -p placeholder-plugin.yaml
```

Use `--phase both` — it runs the mark-and-convert in a single pass over the
rendered HTML. (The separate `--phase markdown` then `--phase html` flow does
**not** work for editable placeholders: each invocation generates a different
internal marker ID, so the HTML phase can't match the markdown phase.)

The CLI writes two assets into the site — reference them in your config so they
load on every page:

```toml
[project]
extra_css = [ "assets/stylesheets/placeholders.css" ]
extra_javascript = [ "assets/javascripts/placeholder-combined.js" ]
```

> **Gotcha — quote `@VAR@` in YAML code blocks.** A placeholder is only wrapped
> when `@VAR@` is a *contiguous* string in the rendered HTML. The YAML syntax
> highlighter splits unquoted values like `image: @REGISTRY@/app` (because `@`
> is a reserved YAML indicator), so the token stays literal. Quote it —
> `image: "@REGISTRY@/app"` — and it wraps correctly.

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
