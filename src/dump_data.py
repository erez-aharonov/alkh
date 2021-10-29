# import copy
import inspect
import pandas as pd
import types
import re
import pickle


def dump_stack(pickle_file_path='dump.pkl'):
    stack_tuples_list = [(frame.filename, frame.function, frame.lineno, frame) for frame in inspect.stack()]
    raw_stack_df = pd.DataFrame(stack_tuples_list, columns=['file_path', 'function', 'lineno', 'frame'])
    relevant_stack_df = \
        raw_stack_df[~(raw_stack_df['file_path'].str.contains('ipython') |
                       raw_stack_df['file_path'].str.contains('pycharm') |
                       raw_stack_df['file_path'].str.contains('site') |
                       raw_stack_df['file_path'].str.contains('al_khwarizmi/src/dump_data'))].copy()
    relevant_stack_df['locals'] = _get_data_frame_locals(relevant_stack_df)
    locals_stack_df = relevant_stack_df[['file_path', 'function', 'lineno', 'locals']].reset_index(drop=True)
    locals_stack_df.to_pickle(pickle_file_path)


def _get_data_frame_locals(df):
    def _get_relevant_locals(locals_dict):
        list_to_remove = [
            'self',
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

        relevant_locals_dict = {}

        for key in locals_dict.keys():
            cond1 = not re.search('_i[0-9]+', key)
            cond2 = key not in list_to_remove
            cond3 = not isinstance(locals_dict[key], types.ModuleType)
            cond4 = not isinstance(locals_dict[key], types.FunctionType)
            cond5 = not isinstance(locals_dict[key], type)
            if cond1 and cond2 and cond3 and cond4 and cond5:
                try:
                    pickle.dumps(locals_dict[key])
                    relevant_locals_dict[key] = locals_dict[key]
                except (pickle.PickleError, TypeError):
                    pass

        return relevant_locals_dict

    def _get_frame_locals(a_frame):
        frame_locals = a_frame.frame.f_locals
        frame_locals_2 = _get_relevant_locals(frame_locals)
        return frame_locals_2

    locals_series = df['frame'].apply(_get_frame_locals)
    return locals_series
