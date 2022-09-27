import sys
import streamlit as st
import streamlit.components.v1 as components
from alkh import cst_utils
from alkh import app_utils


assert len(sys.argv) in [2]

file_path = sys.argv[1]

file_lines = open(file_path).readlines()
file_content = "".join(file_lines)

call_graph_manager = cst_utils.CallGraphManager(file_path)

line_number = st.sidebar.number_input('line number', min_value=1, max_value=len(file_lines))
variable_name = cst_utils.get_variable_name(file_lines[int(line_number) - 1])
if variable_name is None:
    variable_name = "None"
    lines_numbers_list = [line_number]
    lines_numbers_string = line_number
else:
    lines_numbers_list = call_graph_manager.get_variable_affecting_lines_numbers(line_number)
    lines_numbers_string = ",".join(map(str, lines_numbers_list))

st.sidebar.text(f"variable name: {variable_name}")
focus_state = st.sidebar.radio("focus", ["off", "on"])

if focus_state == "off":
    html = app_utils.get_full_code_html(lines_numbers_list, file_content)
else:
    html = app_utils.get_focused_code_html(lines_numbers_list, file_lines)

components.html(html, height=400, width=800, scrolling=True)
