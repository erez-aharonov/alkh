import streamlit as st
import streamlit.components.v1 as components


file_path = '/mnt/hgfs/dev/open_source_projects/alkh/notebooks/play.py'
lines = open(file_path).read()

prism_twilight_min_css_file_path = "./notebooks/prism-twilight.min.css"
prism_twilight_min_css_string = open(prism_twilight_min_css_file_path).read()

html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>{prism_twilight_min_css_string}</style>
	<link href="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/plugins/line-numbers/prism-line-numbers.min.css" rel="stylesheet" />
	<link href="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/plugins/line-highlight/prism-line-highlight.min.css" rel="stylesheet" />		
</head>
<body class="line-numbers"> 
	<header data-plugin-header="line-highlight"></header>
	<pre class="language-python" data-line="1, 6, 8, 9"><code>{lines}</code></pre>
	<script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/prism.min.js"></script>
	<script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/plugins/autoloader/prism-autoloader.min.js"></script>
	<script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/plugins/line-numbers/prism-line-numbers.min.js"></script>		
	<script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/plugins/line-highlight/prism-line-highlight.min.js"></script>
</body>
</html>
"""

components.html(html, height=600, scrolling=True)
