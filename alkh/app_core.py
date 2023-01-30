import os
from typing import *
import numpy as np


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


def get_full_code_html(lines_numbers_list, file_content):
    lines_numbers_string = _convert_list_of_number_to_string(lines_numbers_list)
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
    <script>{_read_script_file("prism-python.min.js")}</script>
</body>
</html>
"""
    return html


def get_focused_code_html(lines_numbers_list: List[int], file_lines_list: List[str]):
    file_lines_array = np.array(file_lines_list)
    lines_numbers_array = np.array(lines_numbers_list)
    relevant_file_lines_list = file_lines_array[lines_numbers_array - 1]
    file_content = "".join(relevant_file_lines_list)
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>{_read_css_file('prism-twilight.min.css')}</style>
</head>
<body class="line-numbers"> 
    <header data-plugin-header="line-highlight"></header>
    <pre class="language-python""><code>{file_content}</code></pre>
    <script>{_read_script_file("prism.min.js")}</script>
    <script>{_read_script_file("prism-python.min.js")}</script>      
</body>
</html>
"""
    return html


def _convert_list_of_number_to_string(lines_numbers_list):
    if len(lines_numbers_list) == 1:
        lines_numbers_string = str(lines_numbers_list[0])
    else:
        lines_numbers_string = ",".join(map(str, lines_numbers_list))
    return lines_numbers_string
