from typing import *
import libcst as cst
import networkx as nx
import pandas as pd


def get_variable_name(a_line: str):
    try:
        line_cst = cst.parse_module(a_line.strip())
        collector = AssignCollector()
        line_cst.visit(collector)
        if not collector.names:
            return None
        elif not collector.names[0]:
            return None
        else:
            variable_name = collector.names[0][0]
            return variable_name
    except:
        return None


class CallGraphManager:
    def __init__(self, file_path):
        self._call_graph, self._call_df = self._get_call_graph_with_df(file_path)

    def get_variable_affecting_lines_numbers(self, variable_name: str) -> List[int]:
        ancestors = nx.ancestors(self._call_graph, variable_name)
        ancestors_df = self._get_ancestors_call_df(ancestors, variable_name)
        lines_numbers_list = self._get_lines_numbers_list(ancestors_df)
        return lines_numbers_list

    def _get_ancestors_call_df(self, ancestors, variable_name):
        return self._call_df[self._call_df['assigned'].isin(ancestors.union({variable_name}))]

    @staticmethod
    def _get_lines_numbers_list(ancestors_df: pd.DataFrame):
        return list(ancestors_df['line'].values)

    def _get_call_graph_with_df(self, file_path: str) -> (nx.DiGraph, pd.DataFrame):
        file_cst = cst.parse_module(open(file_path, 'r').read())
        visitor = FunctionCollector()
        wrapper = cst.metadata.MetadataWrapper(file_cst)
        wrapper.visit(visitor)
        call_df = pd.DataFrame(visitor.get_info(), columns=['assigned', 'data', 'line'])
        call_df['assignee'] = call_df['data'].apply(lambda x: x['names'])
        di_graph = self._create_di_graph_from_call_df(call_df)
        return di_graph, call_df

    def _create_di_graph_from_call_df(self, call_df):
        var_names = self._get_all_variables_names(call_df)
        di_graph = nx.DiGraph()
        for name in var_names:
            di_graph.add_node(name)
        for index, a_series in call_df.iterrows():
            if a_series['assignee']:
                for assignee in a_series['assignee']:
                    di_graph.add_edge(assignee, a_series['assigned'])
        return di_graph

    @staticmethod
    def _get_all_variables_names(call_df):
        return set(list(call_df['assignee'].explode().dropna().unique()) + list(call_df['assigned'].unique()))


class AssignCollector(cst.CSTVisitor):
    def __init__(self):
        super().__init__()
        self.names: List[List] = []

    def visit_Assign(self, node: cst.FunctionDef) -> None:
        targets = [target.target.value for target in node.targets]
        self.names.append(targets)


class FunctionCollector(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self):
        super().__init__()
        self._assign_info: List[Tuple] = []

    def get_info(self):
        return self._assign_info

    def visit_Assign(self, node: cst.FunctionDef) -> None:
        pos = self.get_metadata(cst.metadata.PositionProvider, node).start
        collector = ValueCollector()
        node.value.visit(collector)
        value_dict = {'names': collector.names, 'ints': collector.ints, 'floats': collector.floats}
        self._assign_info.append((node.targets[0].target.value, value_dict, pos.line))


class ValueCollector(cst.CSTVisitor):
    def __init__(self):
        super().__init__()
        self.names: List[str] = []
        self.ints: List[str] = []
        self.floats: List[str] = []

    def visit_Name(self, node: cst.FunctionDef) -> None:
        self.names.append(node.value)

    def visit_Integer(self, node: cst.FunctionDef) -> None:
        self.ints.append(node.value)

    def visit_Float(self, node: cst.FunctionDef) -> None:
        self.floats.append(node.value)
