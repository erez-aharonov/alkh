import os

dir_path = os.path.dirname(__file__)


def _read_asset_file(dir_name, file_name):
    file_path = os.path.join(dir_path, 'assets', dir_name, file_name)
    file_string = open(file_path).read()
    return file_string


def _read_script_file(file_name: str):
    file_string = _read_asset_file('scripts', file_name)
    return file_string


def _read_css_file(file_name: str):
    file_string = _read_asset_file('css', file_name)
    return file_string


def get_html(lines_numbers_string, file_content):
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>{_read_css_file('prism-twilight.min.css')}</style>
    <style>{_read_css_file('prism-line-highlight.min.css')}</style>
    <style>{_read_css_file('prism-line-numbers.min.css')}</style>
</head>
<body class="line-numbers"> 
    <header data-plugin-header="line-highlight"></header>
    <pre class="language-python" data-line="{lines_numbers_string}"><code>{file_content}</code></pre>
    <script>{_read_script_file("prism.min.js")}</script>     
    <script>{_read_script_file("prism-line-numbers.min.js")}</script>
    <script>{_read_script_file("prism-line-highlight.min.js")}</script>    
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/plugins/autoloader/prism-autoloader.min.js"></script>      
</body>
</html>
"""
    return html
