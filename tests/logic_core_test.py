from alkh.logic_core import CallGraphManager


file_path = '/mnt/dev/open_source_projects/alkh/notebooks/play2.py'
line_number = 5
call_graph_manager = CallGraphManager(file_path)
final_lines_numbers_list = call_graph_manager.get_lines_numbers_affecting_line_number(line_number)
print('final_lines_numbers_list', final_lines_numbers_list)
