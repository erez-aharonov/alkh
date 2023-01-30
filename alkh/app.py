import sys
import streamlit as st
import streamlit.components.v1 as components
from alkh import logic_core
from alkh import app_core


assert len(sys.argv) in [2]

file_path = sys.argv[1]

file_lines = open(file_path).readlines()
file_content = "".join(file_lines)

call_graph_manager = logic_core.CallGraphManager(file_path)

line_number = st.sidebar.number_input('line number', min_value=1, max_value=len(file_lines))

lines_numbers_list = call_graph_manager.get_lines_numbers_affecting_line_number(line_number)
lines_numbers_string = ",".join(map(str, lines_numbers_list))
hocus_tab, focus_tab = st.tabs(["Hocus", "Focus"])

with hocus_tab:
    html = app_core.get_full_code_html(lines_numbers_list, file_content)
    components.html(html, height=400, width=800, scrolling=True)

with focus_tab:
    html = app_core.get_focused_code_html(lines_numbers_list, file_lines)
    components.html(html, height=400, width=800, scrolling=True)
