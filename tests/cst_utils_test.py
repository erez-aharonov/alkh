from alkh.cst_utils import CallGraphManager

file_path = '/mnt/dev/open_source_projects/alkh/notebooks/play.py'
line_number = 19
call_graph_manager = CallGraphManager(file_path)
call_graph_manager.get_variable_affecting_lines_numbers(line_number)
