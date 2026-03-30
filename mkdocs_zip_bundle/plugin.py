"""
MkDocs plugin to bundle specific code blocks into downloadable ZIP or raw files.
"""
import os
import logging
import shutil
import re
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from bs4 import BeautifulSoup

log = logging.getLogger('mkdocs.plugins.zip_bundle')

class ZipBundlePlugin(BasePlugin):
    """
    Plugin class for bundling code blocks.
    """
    config_scheme = (
        ('include_jszip', config_options.Type(bool, default=True)),
        ('zip_label_suffix', config_options.Type(str, default="(.zip)")),
    )

    def on_config(self, config):
        """
        Automatically add our JS and CSS to the project configuration.
        """
        if self.config['include_jszip']:
            js_jszip = 'javascripts/jszip.min.js'
            if js_jszip not in config['extra_javascript']:
                config['extra_javascript'].append(js_jszip)

        js_bundle = 'javascripts/zip-bundle.js'
        if js_bundle not in config['extra_javascript']:
            config['extra_javascript'].append(js_bundle)

        css_bundle = 'css/zip-bundle.css'
        if css_bundle not in config['extra_css']:
            config['extra_css'].append(css_bundle)

        return config

    def _sanitize_filename(self, filename):
        """
        Sanitize filename to prevent path traversal while allowing subdirectories.
        """
        # Replace backslashes with forward slashes for ZIP compatibility
        filename = filename.replace('\\', '/')
        # Remove any ".." segments to prevent traversal
        filename = re.sub(r'\.\.(?=/|$)', '', filename)
        # Remove any leading slashes
        filename = re.sub(r'^/+', '', filename)
        # Collapse multiple slashes
        filename = re.sub(r'/+', '/', filename)
        return filename.strip()

    def _create_button(self, soup, bundle_id, elements):
        """
        Create the download button for a bundle.
        """
        btn = soup.new_tag("button")
        btn['class'] = "md-button zip-bundle-btn"
        btn['data-bundle-id'] = bundle_id
        btn['type'] = "button"
        btn['aria-label'] = f"Download {bundle_id.replace('-', ' ')} bundle"

        # Check for custom label on ANY element in the bundle (first one wins)
        custom_label = next((el.get('data-zip-label') for el in elements if el.get('data-zip-label')), None)
        force_zip = any(el.get('data-zip-force') == 'true' for el in elements)

        if custom_label:
            btn.string = custom_label
        elif len(elements) == 1 and not force_zip:
            filename = elements[0].get('data-zip-filename', 'file')
            # Extract only the base filename for the button label if it's a path
            display_name = os.path.basename(filename)
            btn.string = f"Download {display_name}"
        else:
            label = bundle_id.replace('-', ' ').title()
            suffix = self.config['zip_label_suffix']
            btn.string = f"Download {label} {suffix}".strip()

        container = soup.new_tag("div")
        container['class'] = "zip-bundle-container"
        container.append(btn)
        return container

    def on_page_content(self, html, page, config, files):
        """
        Inject download buttons into the page content.
        """
        if "data-zip-bundle" not in html:
            return html

        soup = BeautifulSoup(html, 'html.parser')

        # 1. Group all elements by their bundle ID
        bundles = {}
        for el in soup.find_all(attrs={"data-zip-bundle": True}):
            bundle_id = el['data-zip-bundle']
            if bundle_id not in bundles:
                bundles[bundle_id] = []
            
            # Sanitize filename on the element before grouping
            if el.has_attr('data-zip-filename'):
                el['data-zip-filename'] = self._sanitize_filename(el['data-zip-filename'])
            
            bundles[bundle_id].append(el)

        if not bundles:
            return html

        # 2. For each bundle, inject a download button after the last element
        for bundle_id, elements in bundles.items():
            container = self._create_button(soup, bundle_id, elements)
            elements[-1].insert_after(container)

        return str(soup)

    def on_post_build(self, config):
        """
        Copy assets to the site directory after build.
        """
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        
        to_copy = ['zip-bundle.js', 'zip-bundle.css']
        if self.config['include_jszip']:
            to_copy.append('jszip.min.js')

        for filename in to_copy:
            subfolder = 'javascripts' if filename.endswith('.js') else 'css'
            dest_path = os.path.join(config['site_dir'], subfolder, filename)
            src_path = os.path.join(assets_dir, filename)

            if not os.path.exists(src_path):
                raise FileNotFoundError(
                    f"ZipBundle: Asset '{filename}' not found in package at {src_path}. "
                    "Your installation may be corrupt — try reinstalling mkdocs-zip-bundle."
                )

            try:
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copyfile(src_path, dest_path)
            except OSError as e:
                raise OSError(
                    f"ZipBundle: Failed to copy '{filename}' to {dest_path}: {e}. "
                    "Downloads will not work in the built site."
                ) from e
