# Changelog

## 0.2.0 — 2026-05-30

### Added
- **Zensical support.** Download buttons are now injected client-side, so the
  plugin works on [Zensical](https://zensical.org) — and any generator — by
  loading the assets via `extra_javascript` / `extra_css`, with no MkDocs
  plugin hook required. See "Using with Zensical" in the configuration docs.

### Changed
- Button creation moved from the Python `on_page_content` hook into
  `zip-bundle.js`. The injection subscribes to the `document$` observable
  (instant-navigation safe) and is idempotent — on MkDocs/Material it sees the
  server-injected buttons and no-ops, so existing behavior is unchanged.
- Package description and keywords updated to reflect MkDocs/Material **and**
  Zensical.

### Known limitations
- **`mkdocs-placeholder-plugin` does not work on Zensical yet.** The live-value
  substitution relies on placeholder *wrapping* that runs at MkDocs build time,
  which Zensical doesn't run. The ZIP/download itself works on Zensical, but the
  downloaded files contain the literal template text (e.g. `@PORT@`) rather than
  the reader's values. Works fully on MkDocs/Material.

## 0.1.1

- Initial published release.
