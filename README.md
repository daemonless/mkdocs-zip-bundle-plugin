# mkdocs-zip-bundle-plugin

Turn code blocks into downloadable files — for **MkDocs/Material** and **[Zensical](https://zensical.org)**. Tag any code block with a bundle ID and filename and a download button is injected automatically. Works with single files (direct download) or multiple files (ZIP archive).

Built to pair with [`mkdocs-placeholder-plugin`](https://github.com/six-two/mkdocs-placeholder-plugin): if your docs use interactive placeholders like `@PORT@`, the downloaded file will contain the user's actual values, not the defaults. _(MkDocs/Material — see [Using with Zensical](https://mkdocs-zip-bundle-plugin.daemonless.io/configuration/#using-with-zensical) for the Zensical caveat.)_

**[Live demo → mkdocs-zip-bundle-plugin.daemonless.io](https://mkdocs-zip-bundle-plugin.daemonless.io)**

## Features

- **Single file downloads** — one code block gets a direct raw file download, no ZIP needed
- **Multi-file ZIP bundles** — group multiple code blocks into one ZIP with a single button
- **Placeholder-aware** — captures the live browser state, so user-edited values are included in the download
- **Nested paths** — use `configs/app.yaml` as a filename to create subdirectories inside the ZIP
- **Custom button labels** — override auto-generated text per bundle
- **Self-contained** — ships with JSZip and default styling, no extra dependencies

## Installation

```bash
pip install mkdocs-zip-bundle-plugin
```

Requires Python 3.8+ and MkDocs 1.4+. Download buttons require a modern browser (Chrome, Firefox, Safari, Edge).

## Configuration

```yaml
plugins:
  - search
  - zip-bundle:
      include_jszip: true   # set to false if you already load JSZip elsewhere
      zip_label_suffix: "(.zip)"  # appended to multi-file bundle button labels
```

Also enable the `attr_list` extension so MkDocs can read attributes on code blocks:

```yaml
markdown_extensions:
  - attr_list
  - pymdownx.superfences  # recommended for reliable attribute support
```

## Usage

Add `data-zip-bundle` and `data-zip-filename` attributes to any fenced code block:

### Single file

    ```yaml { data-zip-bundle="my-app" data-zip-filename="compose.yaml" }
    services:
      app:
        image: my-image:latest
    ```

The plugin injects a **Download compose.yaml** button directly after the code block.

### Multiple files (ZIP)

    ```yaml { data-zip-bundle="my-app" data-zip-filename="compose.yaml" }
    services:
      app:
        image: my-image:latest
    ```

    ```bash { data-zip-bundle="my-app" data-zip-filename="setup.sh" }
    mkdir -p /data/app
    ```

Both blocks share the same bundle ID. The plugin injects a single **Download My App (.zip)** button after the last block.

### Custom button label

    ```yaml { data-zip-bundle="my-app" data-zip-filename="compose.yaml" data-zip-label="Download config" }
    ...
    ```

### Force ZIP for a single file

    ```yaml { data-zip-bundle="my-app" data-zip-filename="compose.yaml" data-zip-force="true" }
    ...
    ```

### Nested directories

    ```yaml { data-zip-bundle="my-app" data-zip-filename="config/app.yaml" }
    ...
    ```

    ```bash { data-zip-bundle="my-app" data-zip-filename="scripts/setup.sh" }
    ...
    ```

The ZIP will contain `config/app.yaml` and `scripts/setup.sh` preserving the directory structure.

## How it works with placeholders

If you use [`mkdocs-placeholder-plugin`](https://github.com/six-two/mkdocs-placeholder-plugin), your docs can have editable values like `@PORT@` or `@DATA_PATH@` that users customize in the browser.

When the user clicks a download button from this plugin, the downloaded file contains whatever is currently in the code block — including any values the user has already changed. This makes it possible to offer personalized, copy-paste-ready config files directly from your documentation.

## License

MIT — see [LICENSE](LICENSE) for details. Bundles [JSZip](https://github.com/Stuk/jszip) (MIT).
