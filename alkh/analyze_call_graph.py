import subprocess
import sys
import os
import alkh
import inspect
import pandas as pd


alkh_dir_path = os.path.dirname(alkh.__file__)
app_file_path = os.path.join(alkh_dir_path, 'app.py')


def analyze():
    file_names_list = [frame.filename for frame in inspect.stack()]
    file_names_series = pd.Series(file_names_list)
    ignore_stack_list = \
        ['ipython', 'pycharm', 'site-packages', 'pydev', r'alkh\\analyze_call_graph.py', 'alkh/analyze_call_graph.py']
    relevant_file_names_series = file_names_series[~file_names_series.str.contains('|'.join(ignore_stack_list))].copy()
    caller_file_path = relevant_file_names_series.iloc[0]
    subprocess.run([f"{sys.executable}", "-m", "streamlit", "run", app_file_path, "--", caller_file_path])
