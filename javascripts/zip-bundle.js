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
