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
    lines_numbers_string = line_number
else:
    lines_numbers_list = call_graph_manager.get_variable_affecting_lines(variable_name)
    lines_numbers_string = ",".join(map(str, lines_numbers_list))

st.sidebar.text(f"variable name: {variable_name}")

html = app_utils.get_html(lines_numbers_string, file_content)

components.html(html, height=800, scrolling=True)
