from typing import *
import libcst as cst
import networkx as nx
import numpy as np
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
        self._call_graph, self._call_df, self._scopes_df = self._get_call_graph_with_df(file_path)

    def get_variable_affecting_lines_numbers(self, line_number: str) -> List[int]:
        a_series = self._call_df.query(f"line == {line_number}").iloc[0]
        graph_node_name = a_series['hash_name']
        ancestors = nx.ancestors(self._call_graph, graph_node_name)
        ancestors_df = self._get_ancestors_call_df(ancestors, graph_node_name)
        lines_numbers_list = self._get_lines_numbers_list(ancestors_df)
        scope_hierarchy_starts_list = self._get_scope_hierarchy_starts_list(line_number, self._scopes_df)
        final_lines_numbers_list = list(np.sort(np.array(scope_hierarchy_starts_list + lines_numbers_list)))
        return final_lines_numbers_list

    @staticmethod
    def _get_scope_hierarchy_starts_list(line_number, scopes_df):
        query_string = f"start_line_number <= {line_number} and end_line_number >= {line_number}"
        all_scopes_df = scopes_df.query(query_string).sort_values("length")
        relevant_rows_df = all_scopes_df.iloc[:-1]
        temp_series = \
            relevant_rows_df.apply(
                lambda x: list(range(x["start_line_number"], x["header_end_line_number"] + 1)),
                axis=1)
        lines_numbers_list = list(temp_series.explode().sort_values())
        return lines_numbers_list

    def _get_ancestors_call_df(self, ancestors, graph_node_name):
        return self._call_df[self._call_df['hash_name'].isin(ancestors.union({graph_node_name}))]

    @staticmethod
    def _get_lines_numbers_list(ancestors_df: pd.DataFrame):
        return list(ancestors_df['line'].values)

    def _get_call_graph_with_df(self, file_path: str) -> (nx.DiGraph, pd.DataFrame):
        file_lines = open(file_path, 'r').readlines()
        file_content = open(file_path, 'r').read()
        wrapper = cst.metadata.MetadataWrapper(cst.parse_module(file_content))
        scopes = set(wrapper.resolve(cst.metadata.ScopeProvider).values())
        ranges = wrapper.resolve(cst.metadata.PositionProvider)
        file_number_of_lines = len(file_lines)

        a = pd.Series(list(scopes)).to_frame('scope')
        scopes_df = a["scope"].apply(self._get_range, args=(file_number_of_lines, ranges))
        scopes_df["scope_index"] = range(len(scopes_df))

        di_graph, call_df = self._get_call_graph_with_df_from_objects(wrapper, ranges, scopes_df)
        return di_graph, call_df, scopes_df

    @staticmethod
    def _get_range(scope, file_number_of_lines, ranges):
        if isinstance(scope, cst.metadata.scope_provider.GlobalScope):
            start_line_number = 1
            end_line_number = file_number_of_lines
            scope_name = 'global'
            header_end_line_number = start_line_number
        else:
            start_line_number = ranges[scope.node].start.line
            if hasattr(scope.node, 'decorators') and scope.node.decorators:
                start_line_number = max([ranges[decorator].start.line for decorator in scope.node.decorators])

            end_line_number = ranges[scope.node].end.line
            scope_name = scope.name
            header_end_line_number = start_line_number
            if hasattr(scope.node, 'params') and scope.node.params:
                header_end_line_number = ranges[scope.node.params].end.line
            if hasattr(scope.node, 'returns') and scope.node.returns:
                header_end_line_number = ranges[scope.node.returns].end.line
        scope_length = end_line_number - start_line_number + 1
        values = [scope, start_line_number, end_line_number, header_end_line_number, scope_length, scope_name]
        names = ["scope", "start_line_number", "end_line_number", "header_end_line_number", "length", "name"]
        output_series = pd.Series(values, index=names)
        return output_series

    def _get_call_graph_with_df_from_objects(self, wrapper, ranges, scopes_df) -> (nx.DiGraph, pd.DataFrame):
        visitor = FunctionCollector(ranges)
        wrapper.visit(visitor)
        call_df = pd.DataFrame(visitor.get_info(), columns=['assigned', 'data', 'line'])
        call_df['assigner'] = call_df['data'].apply(lambda x: x['names'])
        call_df["scope_index"] = call_df["line"].apply(self._get_scope_index, args=(scopes_df,))
        call_df['hash_name'] = call_df.apply(lambda x: (x["assigned"], x["scope_index"]), axis=1)
        di_graph = self._create_di_graph_from_call_df(call_df)
        return di_graph, call_df

    @staticmethod
    def _get_all_variables_names(call_df):
        assigned_list = list(call_df.apply(lambda x: (x["assigned"], x["scope_index"]), axis=1))
        assigners_list = list(
            call_df.explode(['assigner']).dropna().apply(lambda x: (x["assigner"], x["scope_index"]), axis=1))
        return set(assigned_list + assigners_list)

    def _create_di_graph_from_call_df(self, call_df):
        var_names = self._get_all_variables_names(call_df)
        di_graph = nx.DiGraph()
        for name in var_names:
            di_graph.add_node(name)
        for index, a_series in call_df.iterrows():
            scope_index = a_series["scope_index"]
            if a_series['assigner']:
                for assigner in a_series['assigner']:
                    di_graph.add_edge((assigner, scope_index), (a_series['assigned'], scope_index))
        return di_graph

    @staticmethod
    def _get_scope_index(line_number, scopes_df):
        c = scopes_df.query(f"start_line_number <= {line_number} and end_line_number >= {line_number}").sort_values(
            "length")
        scope_index = c.iloc[0]['scope_index']
        return scope_index


class AssignCollector(cst.CSTVisitor):
    def __init__(self):
        super().__init__()
        self.names: List[List] = []

    def visit_Assign(self, node: cst.FunctionDef) -> None:
        targets = [target.target.value for target in node.targets]
        self.names.append(targets)


class FunctionCollector(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self, ranges):
        super().__init__()
        self._ranges = ranges
        self._assign_info: List[Tuple] = []

    def get_info(self):
        return self._assign_info

    def visit_Assign(self, node: cst.FunctionDef) -> None:
        pos = self._ranges[node].start
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
