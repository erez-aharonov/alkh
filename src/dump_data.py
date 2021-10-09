import copy
import inspect
import pandas as pd
import types
import re


def dump_stack(pickle_file_path='dump.pkl'):
    stack_tuples_list = [(frame.filename, frame.function, frame.lineno, frame) for frame in inspect.stack()]
    raw_stack_df = pd.DataFrame(stack_tuples_list, columns=['file_path', 'function', 'lineno', 'frame'])
    relevant_stack_df = \
        raw_stack_df[~(raw_stack_df['file_path'].str.contains('ipython') |
                       raw_stack_df['file_path'].str.contains('pycharm') |
                       raw_stack_df['file_path'].str.contains('site') |
                       raw_stack_df['file_path'].str.contains('al-khwarizmi/src/dump_data'))].copy()
    relevant_stack_df['locals'] = _get_data_frame_locals(relevant_stack_df)
    locals_stack_df = relevant_stack_df[['file_path', 'function', 'lineno', 'locals']].reset_index(drop=True)
    locals_stack_df.to_pickle(pickle_file_path)


def _get_data_frame_locals(df):
    def _remove_reserved_locals(locals_dict):
        locals_dict_copy = copy.copy(locals_dict)
        list_to_remove = [
            '__name__',
            '__doc__',
            '__package__',
            '__loader__',
            '__spec__',
            '__file__',
            '__builtins__',
            '__builtin__',
            '_ih',
            '_oh',
            '_dh',
            'In',
            'Out',
            'get_ipython',
            'exit',
            'quit',
            '_',
            '__',
            '___',
            '_i',
            '_ii',
            '_iii']

        for key in locals_dict.keys():
            if re.search('_i[0-9]+', key):
                del locals_dict_copy[key]

        for key in list_to_remove:
            if key in locals_dict_copy.keys():
                del locals_dict_copy[key]

        return locals_dict_copy

    def _remove_functions(locals_dict):
        locals_dict_copy = copy.copy(locals_dict)
        for key in locals_dict.keys():
            if isinstance(locals_dict_copy[key], types.FunctionType):
                del locals_dict_copy[key]
        return locals_dict_copy

    def _get_frame_locals(a_frame):
        frame_locals = a_frame.frame.f_locals
        frame_locals_2 = _remove_reserved_locals(frame_locals)
        frame_locals_3 = _remove_functions(frame_locals_2)
        return frame_locals_3

    locals_series = df['frame'].apply(_get_frame_locals)
    return locals_series
