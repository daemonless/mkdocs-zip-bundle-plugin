// ── Button injection ──────────────────────────────────────────────────
// Mirrors the Python plugin's on_page_content / _create_button so the
// download buttons exist even where the plugin's build hook never runs
// (e.g. Zensical). Idempotent: skips any bundle that already has a button,
// so on MkDocs/Material (server-injected) this is a harmless no-op.

function sanitizeFilename(filename) {
    // Match plugin._sanitize_filename: prevent path traversal, allow subdirs.
    filename = filename.replace(/\\/g, '/');     // backslashes -> forward
    filename = filename.replace(/\.\.(?=\/|$)/g, '');  // drop ".." segments
    filename = filename.replace(/^\/+/, '');     // no leading slashes
    filename = filename.replace(/\/+/g, '/');    // collapse slashes
    return filename.trim();
}

function titleCase(str) {
    // Python str.title(): capitalize each word, lowercase the rest.
    return str.replace(/\w\S*/g, t => t.charAt(0).toUpperCase() + t.slice(1).toLowerCase());
}

function buildButtonContainer(bundleId, elements) {
    const cfg = window.zipBundleConfig || {};
    const labelSuffix = cfg.labelSuffix || '(.zip)';

    const btn = document.createElement('button');
    btn.className = 'md-button zip-bundle-btn';
    btn.setAttribute('data-bundle-id', bundleId);
    btn.type = 'button';
    btn.setAttribute('aria-label', `Download ${bundleId.replace(/-/g, ' ')} bundle`);

    const customLabel = elements
        .map(el => el.getAttribute('data-zip-label'))
        .find(Boolean);
    const forceZip = elements.some(el => el.getAttribute('data-zip-force') === 'true');

    if (customLabel) {
        btn.textContent = customLabel;
    } else if (elements.length === 1 && !forceZip) {
        const filename = elements[0].getAttribute('data-zip-filename') || 'file';
        const displayName = filename.split('/').pop();  // basename
        btn.textContent = `Download ${displayName}`;
    } else {
        const label = titleCase(bundleId.replace(/-/g, ' '));
        btn.textContent = `Download ${label} ${labelSuffix}`.trim();
    }

    const container = document.createElement('div');
    container.className = 'zip-bundle-container';
    container.appendChild(btn);
    return container;
}

function injectZipButtons() {
    const tagged = document.querySelectorAll('[data-zip-bundle]');
    if (tagged.length === 0) return;

    // Group elements by bundle id, preserving document order.
    const bundles = new Map();
    tagged.forEach(el => {
        if (el.hasAttribute('data-zip-filename')) {
            el.setAttribute('data-zip-filename',
                sanitizeFilename(el.getAttribute('data-zip-filename')));
        }
        const id = el.getAttribute('data-zip-bundle');
        if (!bundles.has(id)) bundles.set(id, []);
        bundles.get(id).push(el);
    });

    bundles.forEach((elements, id) => {
        // Idempotent: skip if a button already exists (server-injected or a
        // prior run under instant navigation).
        const sel = `.zip-bundle-btn[data-bundle-id="${CSS.escape(id)}"]`;
        if (document.querySelector(sel)) return;
        const container = buildButtonContainer(id, elements);
        elements[elements.length - 1].insertAdjacentElement('afterend', container);
    });
}

// Run on initial load and on every (instant) navigation. Material/Zensical
// expose the document$ observable; fall back to DOMContentLoaded elsewhere.
if (window.document$ && typeof window.document$.subscribe === 'function') {
    window.document$.subscribe(injectZipButtons);
} else if (document.readyState !== 'loading') {
    injectZipButtons();
} else {
    document.addEventListener('DOMContentLoaded', injectZipButtons);
}

// ── Download handling ─────────────────────────────────────────────────

document.addEventListener('click', function(e) {
    const btn = e.target.closest('.zip-bundle-btn[data-bundle-id]');
    if (btn) {
        downloadZipBundle(btn.getAttribute('data-bundle-id'));
    }
});

async function downloadZipBundle(bundleId) {
    const elements = document.querySelectorAll(`[data-zip-bundle="${bundleId}"]`);

    if (elements.length === 0) {
        console.warn(`No elements found for bundle ID: ${bundleId}`);
        return;
    }

    const forceZip = Array.from(elements).some(el => el.getAttribute('data-zip-force') === 'true');

    // If it's only one file AND we aren't forcing a ZIP, download it directly
    if (elements.length === 1 && !forceZip) {
        const el = elements[0];
        const filename = el.getAttribute('data-zip-filename') || 'file';
        const codeEl = el.querySelector('code') || el;
        const content = codeEl.innerText;

        // Ensure UTF-8 encoding
        const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        triggerDownload(url, filename);
        return;
    }

    // Multiple files (or forced single ZIP)
    if (typeof JSZip === 'undefined') {
        console.error('JSZip is not loaded. Please include it in your mkdocs.yml extra_javascript or enable it in the plugin config.');
        alert('Error: ZIP library not loaded.');
        return;
    }

    const zip = new JSZip();
    elements.forEach(el => {
        const filename = el.getAttribute('data-zip-filename') || 'unnamed-file';
        const codeEl = el.querySelector('code') || el;
        const content = codeEl.innerText;

        // Skip empty files if they have no content
        if (content.trim().length === 0) {
            console.warn(`Skipping empty file: ${filename}`);
            return;
        }

        zip.file(filename, content);
    });

    const blob = await zip.generateAsync({type: "blob"});
    const url = URL.createObjectURL(blob);
    triggerDownload(url, `${bundleId}.zip`);
}

function triggerDownload(url, filename) {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
