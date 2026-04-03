# mkdocs-zip-bundle-plugin

Turn code blocks into **downloadable files** — directly from your MkDocs docs. Tag any fenced code block with a bundle ID and filename and the plugin injects a download button. Group multiple blocks under one ID to produce a **ZIP archive**. Pair with [`mkdocs-placeholder-plugin`](https://github.com/six-two/mkdocs-placeholder-plugin) and the downloaded files contain the reader's own values, not your defaults.

---

## Live demo

Edit the fields below. Every code block on this page updates live. Click any download button — the file you get has **your values** in it, not the defaults.

<div class="auto-input-table" data-columns="description,input"></div>

---

### Single file download

Add `data-zip-bundle` and `data-zip-filename` to a code block. The plugin injects a download button — no ZIP, just the raw file.

~~~markdown
```yaml { data-zip-bundle="compose-only" data-zip-filename="compose.yaml" }
services:
  @APP_NAME@:
    ...
```
~~~

**Result:**

```yaml { data-zip-bundle="compose-only" data-zip-filename="compose.yaml" }
services:
  @APP_NAME@:
    image: ghcr.io/example/@APP_NAME@:latest
    container_name: @APP_NAME@
    environment:
      - PUID=@PUID@
      - PGID=@PGID@
      - TZ=@TZ@
    ports:
      - "@PORT@:8080"
    volumes:
      - @CONFIG_PATH@:/config
    restart: unless-stopped
```

---

### Multi-file ZIP bundle

Use the **same `data-zip-bundle` ID** on multiple blocks. The button appears after the last one and downloads all files as a single ZIP.

~~~markdown
```yaml { data-zip-bundle="full-bundle" data-zip-filename="compose.yaml" }
...
```

```ini { data-zip-bundle="full-bundle" data-zip-filename="app.env" }
...
```

```bash { data-zip-bundle="full-bundle" data-zip-filename="setup.sh" }
...
```
~~~

**Result:**

```yaml { data-zip-bundle="full-bundle" data-zip-filename="compose.yaml" }
services:
  @APP_NAME@:
    image: ghcr.io/example/@APP_NAME@:latest
    container_name: @APP_NAME@
    environment:
      - PUID=@PUID@
      - PGID=@PGID@
      - TZ=@TZ@
    ports:
      - "@PORT@:8080"
    volumes:
      - @CONFIG_PATH@:/config
    restart: unless-stopped
```

```ini { data-zip-bundle="full-bundle" data-zip-filename="app.env" }
APP_NAME=@APP_NAME@
HOST=@HOST_IP@
PORT=@PORT@
CONFIG_PATH=@CONFIG_PATH@
TZ=@TZ@
PUID=@PUID@
PGID=@PGID@
```

```bash { data-zip-bundle="full-bundle" data-zip-filename="setup.sh" }
#!/bin/sh
set -e

mkdir -p @CONFIG_PATH@
chown @PUID@:@PGID@ @CONFIG_PATH@

podman compose up -d
echo "Done. Access at http://@HOST_IP@:@PORT@"
```

---

### Nested directories in the ZIP

Use paths as filenames — the plugin creates the directory structure inside the ZIP automatically.

~~~markdown
```yaml { data-zip-bundle="nested" data-zip-filename="config/app.yaml" }
...
```

```bash { data-zip-bundle="nested" data-zip-filename="scripts/setup.sh" }
...
```
~~~

**Result:**

```yaml { data-zip-bundle="nested" data-zip-filename="config/app.yaml" }
server:
  host: @HOST_IP@
  port: @PORT@
  name: @APP_NAME@
timezone: @TZ@
```

```bash { data-zip-bundle="nested" data-zip-filename="scripts/setup.sh" }
#!/bin/sh
mkdir -p @CONFIG_PATH@/config
cp config/app.yaml @CONFIG_PATH@/config/
podman compose up -d
```

---

### Custom button label

Use `data-zip-label` to override the auto-generated button text.

~~~markdown
```yaml { data-zip-bundle="labeled" data-zip-filename="compose.yaml" data-zip-label="Download my config" }
...
```
~~~

**Result:**

```yaml { data-zip-bundle="labeled" data-zip-filename="compose.yaml" data-zip-label="Download my config" }
services:
  @APP_NAME@:
    image: ghcr.io/example/@APP_NAME@:latest
    ports:
      - "@PORT@:8080"
```

---

## Installation

```bash
pip install mkdocs-zip-bundle-plugin mkdocs-placeholder-plugin
```

## Full setup

**`mkdocs.yml`**

```yaml
markdown_extensions:
  - attr_list           # required — reads data-zip-* attributes
  - pymdownx.superfences

plugins:
  - search
  - zip-bundle:
      include_jszip: true
  - placeholder:
      placeholder_file: placeholder-plugin.yaml
```

**`placeholder-plugin.yaml`**

```yaml
settings:
  normal_prefix: "@"
  normal_suffix: "@"
  auto_placeholder_tables: false  # place the table manually where you want it

placeholders:
  APP_NAME:
    default: myapp
    description: Application name
  PORT:
    default: "8080"
    description: Application port
  HOST_IP:
    default: 192.168.1.100
    description: Host IP address
```

**Your page**

Place the input table wherever you want it in your markdown:

```markdown
<div class="auto-input-table" data-columns="description,input"></div>
```

Then tag your code blocks. The download button is injected automatically. At click time, the button reads the **live rendered text** — so whatever the reader typed into the inputs is what ends up in the downloaded file.

[Configuration reference →](configuration.md){ .md-button }
