import os

dir_path = os.path.dirname(__file__)
prism_twilight_min_css_file_path = os.path.join(dir_path, 'assets', 'prism-twilight.min.css')
prism_twilight_min_css_string = open(prism_twilight_min_css_file_path).read()


def get_html(lines_numbers_string, file_content):
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>{prism_twilight_min_css_string}</style>
    <link href="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/plugins/line-numbers/prism-line-numbers.min.css" 
    rel="stylesheet" />
    <link href="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/plugins/line-highlight/prism-line-highlight.min.css" 
    rel="stylesheet" />		
</head>
<body class="line-numbers"> 
    <header data-plugin-header="line-highlight"></header>
    <pre class="language-python" data-line="{lines_numbers_string}"><code>{file_content}</code></pre>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/prism.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/plugins/autoloader/prism-autoloader.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/plugins/line-numbers/prism-line-numbers.min.js"></script>		
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/plugins/line-highlight/prism-line-highlight.min.js">
    </script>
</body>
</html>
"""
    return html
