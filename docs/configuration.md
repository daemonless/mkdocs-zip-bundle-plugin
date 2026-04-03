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
