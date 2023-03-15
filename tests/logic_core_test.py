from alkh.logic_core import CallGraphManager


# file_path = '/mnt/D/tech/repos/alkh/notebooks/play3.py'
# file_path = '/mnt/D/tech/repos/alkh/tests/demo_test.py'
file_path = '/mnt/D/tech/repos/alkh/alkh/logic_core.py'
line_number = 13
call_graph_manager = CallGraphManager(file_path)
final_lines_numbers_list = call_graph_manager.get_lines_numbers_affecting_line_number(line_number)
print('final_lines_numbers_list', final_lines_numbers_list)
