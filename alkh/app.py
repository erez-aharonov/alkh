import argparse
import streamlit as st
import streamlit.components.v1 as components
from alkh import logic_core
from alkh import app_core
from alkh.utils import file_utils


def _main(file_path):
    file_wrapper = file_utils.FileWrapper(file_path)

    uploaded_file = st.sidebar.file_uploader("Please Choose a file", type='py')
    if uploaded_file:
        with st.spinner('Loading file...'):
            file_lines = [bytes_.decode('utf-8') for bytes_ in uploaded_file.readlines()]
            file_wrapper = file_utils.FileWrapper(file_lines)

    call_graph_manager = logic_core.CallGraphManager(file_wrapper)

    line_number = st.sidebar.number_input('line number', min_value=1, max_value=len(file_wrapper.file_lines))

    lines_numbers_list = call_graph_manager.get_lines_numbers_affecting_line_number(line_number)
    hocus_tab, focus_tab = st.tabs(["Hocus", "Focus"])

    with hocus_tab:
        html = app_core.get_full_code_html(lines_numbers_list, file_wrapper.file_content)
        components.html(html, height=400, width=800, scrolling=True)

    with focus_tab:
        html = app_core.get_focused_code_html(lines_numbers_list, file_wrapper.file_lines)
        components.html(html, height=400, width=800, scrolling=True)


def _create_parser():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-f', '--file_path', help='file path to analyze')
    return argument_parser


if __name__ == '__main__':
    parser = _create_parser()
    args = parser.parse_args()
    _main(args.file_path)
