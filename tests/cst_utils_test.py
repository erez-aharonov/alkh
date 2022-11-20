from alkh.cst_utils import CallGraphManager

file_path = '/mnt/dev/open_source_projects/alkh/notebooks/play.py'
line_number = 20
call_graph_manager = CallGraphManager(file_path)
call_graph_manager.get_lines_numbers_affecting_line_number(line_number)
