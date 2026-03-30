import pytest
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

def test_on_page_content_tabbed_placement(plugin):
    # MkDocs Material renders fenced code block attributes onto the .highlight wrapper div
    html = """
    <div class="tabbed-set">
        <div class="tabbed-content">
            <div class="tabbed-block">
                <div class="highlight" data-zip-bundle="b1" data-zip-filename="f1.txt">
                    <pre><code>content</code></pre>
                </div>
            </div>
        </div>
    </div>
    """
    result = plugin.on_page_content(html, None, None, None)
    soup = BeautifulSoup(result, 'html.parser')

    # Button should be INSIDE the tabbed-block, right after the highlight div
    tabbed_block = soup.find(class_='tabbed-block')
    button_container = soup.find(class_='zip-bundle-container')

    assert button_container is not None
    assert button_container.parent == tabbed_block

def test_on_page_content_multi_bundle(plugin):
    html = """
    <div data-zip-bundle="b1" data-zip-filename="f1.txt"></div>
    <div data-zip-bundle="b2" data-zip-filename="f2.txt"></div>
    """
    result = plugin.on_page_content(html, None, None, None)
    soup = BeautifulSoup(result, 'html.parser')
    
    buttons = soup.find_all(class_='zip-bundle-btn')
    assert len(buttons) == 2
    assert buttons[0]['data-bundle-id'] == 'b1'
    assert buttons[1]['data-bundle-id'] == 'b2'

def test_on_config_asset_injection(plugin):
    config = {'extra_javascript': [], 'extra_css': []}
    result = plugin.on_config(config)
    
    assert 'javascripts/jszip.min.js' in result['extra_javascript']
    assert 'javascripts/zip-bundle.js' in result['extra_javascript']
    assert 'css/zip-bundle.css' in result['extra_css']
