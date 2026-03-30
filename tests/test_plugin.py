import os
import shutil
import tempfile
import pytest
from unittest.mock import patch
from bs4 import BeautifulSoup
from mkdocs_zip_bundle.plugin import ZipBundlePlugin


@pytest.fixture
def plugin():
    plugin = ZipBundlePlugin()
    plugin.config = {
        'include_jszip': True,
        'zip_label_suffix': '(.zip)',
    }
    return plugin


def make_element(soup, attrs):
    """Create a real BS4 Tag with the given attributes."""
    tag = soup.new_tag("div")
    for k, v in attrs.items():
        tag[k] = v
    return tag


# --- _sanitize_filename ---

def test_sanitize_filename(plugin):
    assert plugin._sanitize_filename('test.txt') == 'test.txt'
    assert plugin._sanitize_filename('/abs/path/test.txt') == 'abs/path/test.txt'
    assert plugin._sanitize_filename('../traversal.txt') == 'traversal.txt'
    assert plugin._sanitize_filename('some/../../path.txt') == 'some/path.txt'
    assert plugin._sanitize_filename('win\\path.txt') == 'win/path.txt'
    assert plugin._sanitize_filename('subdir/file.txt') == 'subdir/file.txt'
    assert plugin._sanitize_filename('//double//slash//') == 'double/slash/'


# --- _create_button ---

def test_create_button_single(plugin):
    soup = BeautifulSoup('', 'html.parser')
    elements = [make_element(soup, {'data-zip-filename': 'compose.yaml'})]
    container = plugin._create_button(soup, 'my-bundle', elements)

    button = container.find('button')
    assert button.string == 'Download compose.yaml'
    assert button.get('type') == 'button'
    assert 'onclick' not in button.attrs


def test_create_button_single_subdir(plugin):
    soup = BeautifulSoup('', 'html.parser')
    elements = [make_element(soup, {'data-zip-filename': 'configs/compose.yaml'})]
    container = plugin._create_button(soup, 'my-bundle', elements)

    button = container.find('button')
    assert button.string == 'Download compose.yaml'


def test_create_button_custom_label(plugin):
    soup = BeautifulSoup('', 'html.parser')
    elements = [make_element(soup, {'data-zip-filename': 'f.txt', 'data-zip-label': 'Grab Files'})]
    container = plugin._create_button(soup, 'my-bundle', elements)

    button = container.find('button')
    assert button.string == 'Grab Files'


def test_create_button_multi(plugin):
    soup = BeautifulSoup('', 'html.parser')
    elements = [make_element(soup, {}), make_element(soup, {})]
    container = plugin._create_button(soup, 'my-bundle', elements)

    button = container.find('button')
    assert button.string == 'Download My Bundle (.zip)'


def test_create_button_force_zip_single(plugin):
    """Single file with data-zip-force=true should use ZIP label."""
    soup = BeautifulSoup('', 'html.parser')
    elements = [make_element(soup, {'data-zip-filename': 'f.txt', 'data-zip-force': 'true'})]
    container = plugin._create_button(soup, 'my-bundle', elements)

    button = container.find('button')
    assert button.string == 'Download My Bundle (.zip)'


# --- on_post_build ---

@pytest.fixture
def assets_dir():
    return os.path.join(os.path.dirname(__file__), '..', 'mkdocs_zip_bundle', 'assets')


def test_on_post_build_copies_assets(plugin, tmp_path):
    config = {'site_dir': str(tmp_path)}
    plugin.on_post_build(config)

    assert (tmp_path / 'javascripts' / 'jszip.min.js').exists()
    assert (tmp_path / 'javascripts' / 'zip-bundle.js').exists()
    assert (tmp_path / 'css' / 'zip-bundle.css').exists()


def test_on_post_build_skips_jszip_when_disabled(plugin, tmp_path):
    plugin.config['include_jszip'] = False
    config = {'site_dir': str(tmp_path)}
    plugin.on_post_build(config)

    assert not (tmp_path / 'javascripts' / 'jszip.min.js').exists()
    assert (tmp_path / 'javascripts' / 'zip-bundle.js').exists()


def test_on_post_build_missing_asset_raises(plugin, tmp_path):
    config = {'site_dir': str(tmp_path)}
    with patch('os.path.exists', return_value=False):
        with pytest.raises(FileNotFoundError, match='ZipBundle'):
            plugin.on_post_build(config)


def test_on_post_build_copy_failure_raises(plugin, tmp_path):
    config = {'site_dir': str(tmp_path)}
    with patch('shutil.copyfile', side_effect=OSError("disk full")):
        with pytest.raises(OSError, match='ZipBundle'):
            plugin.on_post_build(config)
