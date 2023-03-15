from typing import *
import itertools
import libcst as cst
import networkx as nx
import numpy as np
import pandas as pd
from alkh.utils import code_range_utils


class CallGraphManager:
    def __init__(self, file_path):
        self._calc_base_objects(file_path)
        self._calc_extended_scopes_df()
        self._calc_scopes_df()
        self._calc_assignment_df()
        self._calc_call_df()
        self._calc_dependency_graph()

    def get_lines_numbers_affecting_line_number(self, line_number: int) -> List[int]:
        target_id_to_line_numbers_df = self._target_id_to_line_numbers_df
        lines_contains_series = target_id_to_line_numbers_df['lines_numbers_list'].apply(lambda x: line_number in x)
        line_targets_list = target_id_to_line_numbers_df[lines_contains_series]['target_id'].to_list()
        if line_targets_list:
            final_lines_numbers_list = \
                self._get_lines_numbers_affecting_line_number_with_targets(
                    line_targets_list,
                    target_id_to_line_numbers_df)

        else:
            final_lines_numbers_list = [line_number]

        return final_lines_numbers_list

    def _get_lines_numbers_affecting_line_number_with_targets(self, line_targets_list, target_id_to_line_numbers_df):
        relevant_targets_lines_numbers_list = \
            self._get_relevant_targets_lines_numbers_list(
                line_targets_list,
                target_id_to_line_numbers_df)
        scope_hierarchy_starts_list = \
            self._get_scope_hierarchy_starts_list(
                relevant_targets_lines_numbers_list,
                self._scopes_df)
        a_list = list(set(scope_hierarchy_starts_list + relevant_targets_lines_numbers_list))
        scopes_line_numbers_list = self._get_called_functions_lines(a_list)
        a_list += scopes_line_numbers_list
        a_list = list(set(a_list))
        length = len(a_list)
        proceed = True
        while proceed:
            temp_scopes_line_numbers_list = self._get_called_functions_lines(a_list)
            a_list += temp_scopes_line_numbers_list
            a_list = list(set(a_list))
            new_length = len(a_list)
            proceed = new_length != length
            length = new_length
        final_lines_numbers_list = self._get_sorted_lines_numbers_list(a_list)
        return final_lines_numbers_list

    def _get_called_functions_lines(self, final_lines_numbers_list):
        is_in_lines_series = \
            self._calls_df["node_range"].apply(self._is_call_in_lines, args=(final_lines_numbers_list,))
        a = self._calls_df[is_in_lines_series]
        # noinspection PyTypeHints
        b = a[["scope_index"]].merge(self._scopes_df)
        if not b.empty:
            list_of_lists = b.apply(self._get_whole_scope_lines_numbers, axis=1).tolist()
            concatenated_list = list(itertools.chain(*list_of_lists))
        else:
            concatenated_list = []
        return concatenated_list

    @staticmethod
    def _is_call_in_lines(call_range, final_lines_numbers_list):
        result = any([call_range.start.line <= line <= call_range.end.line for line in final_lines_numbers_list])
        return result

    @staticmethod
    def _get_whole_scope_lines_numbers(scope_series):
        result = list(range(scope_series["start_line_number"], scope_series["end_line_number"] + 1))
        return result

    def _get_relevant_targets_lines_numbers_list(self, line_targets_list, target_id_to_line_numbers_df):
        targets_sets_list = [nx.ancestors(self._dependency_graph, target) for target in line_targets_list]
        influencing_targets_set = set().union(*targets_sets_list)
        relevant_targets_set = influencing_targets_set.union(set(line_targets_list))
        is_relevant_targets_series = \
            target_id_to_line_numbers_df['target_id'].apply(
                self._is_in_targets_set,
                args=(relevant_targets_set,))
        relevant_target_id_to_line_numbers_df = target_id_to_line_numbers_df[is_relevant_targets_series]
        relevant_targets_lines = \
            relevant_target_id_to_line_numbers_df['lines_numbers_list'].explode().sort_values().unique().tolist()
        return relevant_targets_lines

    @staticmethod
    def _is_in_targets_set(target_id, targets_set):
        return target_id in targets_set

    def _calc_base_objects(self, file_path):
        file_lines = open(file_path, 'r').readlines()
        file_content = open(file_path, 'r').read()
        wrapper = cst.metadata.MetadataWrapper(cst.parse_module(file_content))
        scopes = set(wrapper.resolve(cst.metadata.ScopeProvider).values())
        ranges = wrapper.resolve(cst.metadata.PositionProvider)
        file_number_of_lines = len(file_lines)
        self._wrapper = wrapper
        self._scopes = scopes
        self._ranges = ranges
        self._file_number_of_lines = file_number_of_lines

    def _calc_scopes_df(self):
        temp_scopes_df = self._calc_scopes_and_class_scopes_df(self._file_number_of_lines, self._ranges, self._scopes)
        self._extended_scopes_df["scope_index"] = \
            range(len(temp_scopes_df), len(temp_scopes_df) + len(self._extended_scopes_df))
        scopes_df = pd.concat([temp_scopes_df, self._extended_scopes_df]).reset_index(drop=True)
        is_class_scope = scopes_df['scope'].apply(self._is_class_scope)
        class_scopes_df = scopes_df[is_class_scope]
        self._scopes_df = scopes_df
        self._class_scopes_df = class_scopes_df

    def _calc_extended_scopes_df(self):
        collector = ExtendedScopesCollector(self._ranges)
        self._wrapper.visit(collector)
        extended_scopes_df = \
            pd.DataFrame(
                collector.scopes,
                columns=["start_line_number", "header_end_line_number", "end_line_number", "length", "node_range"])
        self._extended_scopes_df = extended_scopes_df

    def _calc_assignment_df(self):
        visitor = AssignCollector(self._ranges)
        self._wrapper.visit(visitor)
        assignment_df = \
            pd.DataFrame(visitor.get_info(), columns=['targets', 'data', 'start_line', 'end_line', 'node_range'])
        assignment_df['sources'] = assignment_df['data'].apply(self._get_sources_from_data)
        assignment_df["scope_index"] = assignment_df["node_range"].apply(self._get_scope_index, args=(self._scopes_df,))
        assignment_df['canonic_targets'] = assignment_df.apply(self._get_canonic_target_list, axis=1)

        scope_to_targets_df, target_id_to_line_numbers_df = self._calc_scope_to_targets_df(assignment_df)

        assignment_df["canonic_sources"] = \
            assignment_df.apply(
                self._get_canonic_source_list,
                args=(scope_to_targets_df,),
                axis=1)
        assignment_df["canonic_targets_ids"] = \
            assignment_df["canonic_targets"].apply(
                self._get_targets_ids_list)

        self._assignment_df = assignment_df
        self._target_id_to_line_numbers_df = target_id_to_line_numbers_df

    @staticmethod
    def _get_targets_ids_list(target_dict_list):
        return [target_dict["id"] for target_dict in target_dict_list]

    def _calc_scope_to_targets_df(self, assignment_df):
        canonic_targets_list = assignment_df["canonic_targets"].explode().tolist()
        canonic_targets_df = pd.DataFrame(canonic_targets_list)
        canonic_targets_df["main_id"] = canonic_targets_df["id"].apply(self._get_main_id)
        canonic_targets_df['lines_numbers_list'] = canonic_targets_df.apply(self._get_lines_range, axis=1)
        canonic_targets_lines_df = \
            canonic_targets_df.groupby(["scope_index", "main_id"])["lines_numbers_list"].apply(
                self._flatten_iterable_of_iterable).reset_index()
        scope_index_to_target_id_df = \
            canonic_targets_lines_df.groupby("scope_index")["main_id"].apply(tuple).reset_index()
        scope_to_targets_df: pd.DataFrame = self._scopes_df.merge(scope_index_to_target_id_df)

        canonic_targets_lines_df['target_id'] = canonic_targets_lines_df.apply(self._get_target_id, axis=1)

        # noinspection PyTypeHints
        target_id_to_line_numbers_df = canonic_targets_lines_df[['target_id', 'lines_numbers_list']]

        return scope_to_targets_df, target_id_to_line_numbers_df

    @staticmethod
    def _get_main_id(id_tuple):
        return id_tuple[1]

    @staticmethod
    def _get_lines_range(a_series):
        lines_range = list(range(a_series['start_line_number'], a_series['end_line_number'] + 1))
        return lines_range

    @staticmethod
    def _flatten_iterable_of_iterable(iterable_of_iterable):
        return list(itertools.chain(*iterable_of_iterable))

    @staticmethod
    def _get_target_id(a_series) -> Tuple:
        return a_series['scope_index'], a_series['main_id']

    def _get_canonic_source_list(self, assignment_series, scope_to_targets_df):
        line_number = assignment_series['start_line']

        canonic_source_list = []
        for source in assignment_series['sources']:
            canonic_source = self._get_canonic_source(source, line_number, scope_to_targets_df)
            if canonic_source is not None:
                canonic_source_list.append(canonic_source)

        return canonic_source_list

    def _get_canonic_source(self, source, line_number, scope_to_targets_df):
        if source[0] == 'self':
            class_scope_index = self._get_scope_index_for_self_objects(line_number, self._class_scopes_df)
            canonic_source = tuple([class_scope_index] + source[1:])
        else:
            query_string = f"start_line_number <= {line_number} and end_line_number >= {line_number}"
            all_scopes_df = scope_to_targets_df.query(query_string).sort_values("length")
            contains_source = all_scopes_df["main_id"].apply(lambda x: source[0] in x)
            contains_source_scopes_df = all_scopes_df[contains_source]
            if not contains_source_scopes_df.empty:
                source_scope_index = contains_source_scopes_df.iloc[0]["scope_index"]
                canonic_source = tuple([source_scope_index] + source)
            else:
                canonic_source = None
        return canonic_source

    @staticmethod
    def _is_class_scope(obj):
        result = isinstance(obj, cst.metadata.scope_provider.ClassScope)
        return result

    @staticmethod
    def _get_sorted_lines_numbers_list(lines_numbers_list):
        return list(np.sort(np.array(lines_numbers_list)))

    def _get_scope_hierarchy_starts_list(self, lines_numbers_list, scopes_df):
        temp_total_lines_numbers_list = []
        for line_number in lines_numbers_list:
            query_string = f"start_line_number <= {line_number} and end_line_number >= {line_number}"
            all_scopes_df = scopes_df.query(query_string).sort_values("length")
            relevant_rows_df = all_scopes_df.iloc[:-1]
            if not relevant_rows_df.empty:
                temp_series = relevant_rows_df.apply(self._get_header_lines_numbers_range, axis=1)
                lines_numbers_list = list(temp_series.explode().sort_values())
                temp_total_lines_numbers_list += lines_numbers_list
        final_lines_numbers_list = list(set(temp_total_lines_numbers_list))
        return final_lines_numbers_list

    @staticmethod
    def _get_header_lines_numbers_range(a_series):
        return list(range(a_series["start_line_number"], a_series["header_end_line_number"] + 1))

    def _get_ancestors_call_df(self, ancestors, graph_node_name):
        return self._assignment_df[self._assignment_df['hash_name'].isin(ancestors.union({graph_node_name}))]

    @staticmethod
    def _get_lines_numbers_list(ancestors_df: pd.DataFrame):
        return list(ancestors_df['start_line'].values)

    def _calc_scopes_and_class_scopes_df(self, file_number_of_lines, ranges, scopes):
        scopes_series = pd.Series(list(scopes)).to_frame('scope')
        scopes_df = scopes_series["scope"].apply(self._get_range, args=(file_number_of_lines, ranges))
        scopes_df["scope_index"] = range(len(scopes_df))
        return scopes_df

    # noinspection PyProtectedMember,PyUnresolvedReferences
    def _get_range(self, scope, file_number_of_lines, ranges):
        if isinstance(scope, cst.metadata.scope_provider.GlobalScope):
            start_line_number = 1
            end_line_number = file_number_of_lines
            scope_name = 'global'
            header_end_line_number = start_line_number
            node_range = \
                cst._position.CodeRange(
                    start=cst._position.CodePosition(line=start_line_number, column=0),
                    end=cst._position.CodePosition(line=end_line_number + 1, column=0))
        else:
            start_line_number = self._get_start_line_number(ranges, scope)
            end_line_number = ranges[scope.node].end.line
            scope_name = scope.name
            header_end_line_number = self._get_header_end_line_number(ranges, scope, start_line_number)
            node_range = ranges[scope.node]
        scope_length = end_line_number - start_line_number + 1
        values = \
            [scope, start_line_number, end_line_number, header_end_line_number, scope_length, scope_name, node_range]
        names = \
            ["scope", "start_line_number", "end_line_number", "header_end_line_number", "length", "name", "node_range"]
        output_series = pd.Series(values, index=names)
        return output_series

    @staticmethod
    def _get_header_end_line_number(ranges, scope, start_line_number):
        header_end_line_number = start_line_number
        if hasattr(scope.node, 'params') and scope.node.params:
            header_end_line_number = ranges[scope.node.params].end.line
        if hasattr(scope.node, 'returns') and scope.node.returns:
            header_end_line_number = ranges[scope.node.returns].end.line
        return header_end_line_number

    @staticmethod
    def _get_start_line_number(ranges, scope):
        start_line_number = ranges[scope.node].start.line
        if hasattr(scope.node, 'decorators') and scope.node.decorators:
            start_line_number = min([ranges[decorator].start.line for decorator in scope.node.decorators])
        return start_line_number

    @staticmethod
    def _get_sources_from_data(a_dict):
        return a_dict['names']

    @staticmethod
    def _get_names_from_data(a_dict):
        return [".".join(j) for j in a_dict['names']]

    def _get_all_variables_names(self, call_df):
        assigned_list = \
            list(call_df.apply(self._get_assigned_variable_scoped_named_tuple, axis=1))
        assigners_list = \
            list(call_df.explode('assigner').dropna().apply(self._get_assigner_variable_scoped_named_tuple, axis=1))
        return set(tuple(assigned_list) + tuple(assigners_list))

    @staticmethod
    def _get_assigned_variable_scoped_named_tuple(a_series) -> Tuple[str, int]:
        return a_series["assigned"], a_series["scope_index"]

    @staticmethod
    def _get_assigner_variable_scoped_named_tuple(a_series) -> Tuple[str, int]:
        return a_series["assigner"], a_series["scope_index"]

    def _calc_dependency_graph(self):
        assignment_df = self._assignment_df
        target_id_to_line_numbers_df = self._target_id_to_line_numbers_df

        di_graph = nx.DiGraph()

        var_names = target_id_to_line_numbers_df['target_id']
        for name in var_names:
            di_graph.add_node(name)

        for index, row_series in assignment_df.iterrows():
            for source in row_series['canonic_sources']:
                for target in row_series['canonic_targets_ids']:
                    di_graph.add_edge(source[:2], target[:2])

        self._dependency_graph = di_graph
        pass

    @staticmethod
    def _get_scope_index_for_self_objects(line_number, scopes_df):
        query_string = f"start_line_number <= {line_number} and end_line_number >= {line_number}"
        relevant_scoped_df = scopes_df.query(query_string).sort_values("length")
        scope_index = relevant_scoped_df.iloc[0]['scope_index']
        return scope_index

    def _get_canonic_target(self, target, start_line_number, end_line_number, scope_index):
        if target[0] == 'self':
            class_scope_index = self._get_scope_index_for_self_objects(start_line_number, self._class_scopes_df)
            target_id = tuple([class_scope_index] + target[1:])
            canonic_target = {'self': True, 'scope_index':  class_scope_index, 'id': target_id}
        else:
            target_id = tuple([scope_index] + target)
            canonic_target = {'self': False, 'scope_index':  scope_index, 'id': target_id}
        canonic_target["start_line_number"] = start_line_number
        canonic_target["end_line_number"] = end_line_number
        return canonic_target

    def _get_canonic_target_list(self, assignment_series):
        scope_index = assignment_series['scope_index']
        start_line_number = assignment_series['start_line']
        end_line_number = assignment_series['end_line']

        canonic_target_list = []
        for target in assignment_series['targets']:
            canonic_target = self._get_canonic_target(target, start_line_number, end_line_number, scope_index)
            canonic_target_list.append(canonic_target)

        return canonic_target_list

    @staticmethod
    def does_scope_contain_assignment(scope_range, assignment_node_range):
        if scope_range is not None:
            result = code_range_utils.check_code_range_a_is_within_b(assignment_node_range, scope_range)
        else:
            result = True
        return result

    def _get_scope_index(self, assignment_node_range, scopes_df):
        does_contain_series = \
            scopes_df["node_range"].apply(self.does_scope_contain_assignment, args=(assignment_node_range,))
        relevant_scoped_df = scopes_df[does_contain_series].sort_values("length")
        scope_index = relevant_scoped_df.iloc[0]['scope_index']
        return scope_index

    def _calc_call_df(self):
        visitor = CallCollector(self._ranges)
        self._wrapper.visit(visitor)
        calls_df = pd.DataFrame(visitor.get_calls(), columns=['target', 'node_range'])
        calls_df["scope_index"] = calls_df.apply(self._get_scope_index_for_call, axis=1)
        self._calls_df = calls_df.dropna()

    def _get_scope_index_for_self_call(self, call_series):
        node_range = call_series["node_range"]
        does_contain_in_class_series = self._class_scopes_df["node_range"].apply(
            code_range_utils.check_code_range_a_contains_b, args=(node_range,))
        containing_class_series = self._class_scopes_df[does_contain_in_class_series].iloc[0]
        is_function_scope_df = self._scopes_df["scope"].apply(
            lambda x: isinstance(x, cst.metadata.scope_provider.FunctionScope))
        functions_scopes_df = self._scopes_df[is_function_scope_df]
        is_function_within_class = functions_scopes_df["node_range"].apply(
            code_range_utils.check_code_range_a_is_within_b, args=(containing_class_series["node_range"],))
        relevant_functions_scopes_df = functions_scopes_df[is_function_within_class]
        does_same_name_series = relevant_functions_scopes_df["name"] == call_series["target"][1]
        relevant_scope_index = relevant_functions_scopes_df[does_same_name_series].iloc[0]["scope_index"]
        return relevant_scope_index

    def _is_function_global(self, node_range):
        is_contained_series = \
            self._scopes_df["node_range"].apply(code_range_utils.check_code_range_a_contains_b, args=(node_range,))
        is_global = is_contained_series.sum() == 2
        return is_global

    def _get_scope_index_for_global_call(self, call_series) -> Optional[int]:
        is_function_scope_df = self._scopes_df["scope"].apply(
            lambda x: isinstance(x, cst.metadata.scope_provider.FunctionScope))
        functions_scopes_df = self._scopes_df[is_function_scope_df]
        is_function_global_series = functions_scopes_df["node_range"].apply(self._is_function_global)
        global_functions_df = functions_scopes_df[is_function_global_series]
        does_same_name_series = global_functions_df["name"] == call_series["target"][0]
        relevant_global_functions_df = global_functions_df[does_same_name_series]
        if not relevant_global_functions_df.empty:
            relevant_scope_index = global_functions_df[does_same_name_series].iloc[0]["scope_index"]
        else:
            relevant_scope_index = None
        return relevant_scope_index

    def _get_scope_index_for_call(self, call_series) -> Optional[int]:
        if call_series["target"][0] == "self":
            scope_index = self._get_scope_index_for_self_call(call_series)
        else:
            scope_index = self._get_scope_index_for_global_call(call_series)
        return scope_index


class AssignCollector(cst.CSTVisitor):
    def __init__(self, ranges):
        super().__init__()
        self._ranges = ranges
        self._assign_info: List[Tuple] = []

    def get_info(self):
        return self._assign_info

    def visit_Assign(self, node: cst.Assign) -> None:
        pos_start = self._ranges[node].start
        pos_end = self._ranges[node].end
        value_collector = ValueCollector()
        node.value.visit(value_collector)
        value_dict = {'names': value_collector.names, 'ints': value_collector.ints, 'floats': value_collector.floats}
        for target in node.targets:
            target_range = self._ranges[target]
            target_collector = ValueCollector()
            target.visit(target_collector)
            names_list = target_collector.names
            if names_list:
                self._assign_info.append(
                    (target_collector.names, value_dict, pos_start.line, pos_end.line, target_range))


class ValueCollector(cst.CSTVisitor):
    def __init__(self):
        super().__init__()
        self.names: List[List] = []
        self.ints: List[str] = []
        self.floats: List[str] = []
        self._attribute_level = 0

    def visit_Name(self, node: cst.FunctionDef) -> None:
        if self._attribute_level == 0:
            self.names.append([node.value])

    def visit_Integer(self, node: cst.FunctionDef) -> None:
        self.ints.append(node.value)

    def visit_Float(self, node: cst.FunctionDef) -> None:
        self.floats.append(node.value)

    def visit_Attribute(self, node: cst.FunctionDef) -> None:
        self._attribute_level += 1

    def visit_Subscript(self, node: cst.FunctionDef) -> None:
        self._attribute_level += 1

    def leave_Attribute(self, node: cst.FunctionDef) -> None:
        if isinstance(node.value, cst.Name):
            self.names.append([node.value.value, node.attr.value])
        elif len(self.names) > 0:
            self.names[len(self.names) - 1].append(node.attr.value)
        self._attribute_level -= 1

    def leave_Subscript(self, node: cst.FunctionDef) -> None:
        if isinstance(node.value, cst.Name):
            self.names.append([node.value.value])
        self._attribute_level -= 1


class ExtendedScopesCollector(cst.CSTVisitor):
    def __init__(self, ranges):
        super().__init__()
        self._ranges = ranges
        self.scopes: List[Tuple] = []

    def visit_If(self, node: cst.If) -> None:
        head_end_line = self._ranges[node.whitespace_after_test].end.line
        self._add_scope(node, head_end_line)

    def visit_Else(self, node: cst.Else) -> None:
        self._common_add_scope(node)

    def visit_With(self, node: cst.With) -> None:
        self._common_add_scope(node)

    def visit_Try(self, node: cst.Try) -> None:
        self._common_add_scope(node)

    def visit_ExceptHandler(self, node: cst.ExceptHandler) -> None:
        self._common_add_scope(node)

    def visit_Finally(self, node: cst.Finally) -> None:
        self._common_add_scope(node)

    def visit_For(self, node: cst.For) -> None:
        self._common_add_scope(node)

    def visit_While(self, node: cst.While) -> None:
        self._common_add_scope(node)

    def _common_add_scope(self, node):
        head_end_line = self._ranges[node.whitespace_before_colon].end.line
        self._add_scope(node, head_end_line)

    def _add_scope(self, node, head_end_line):
        node_range = self._ranges[node]
        start_line = node_range.start.line
        end_line = node_range.end.line
        length = end_line - start_line + 1
        self.scopes.append((start_line, head_end_line, end_line, length, node_range))


class CallCollector(cst.CSTVisitor):
    def __init__(self, ranges):
        super().__init__()
        self._ranges = ranges
        self._calls = []

    def get_calls(self):
        return self._calls

    def visit_Call(self, node: cst.Call) -> None:
        if isinstance(node.func, cst.Name):
            self._calls.append(((node.func.value,), self._ranges[node]))
        elif isinstance(node.func, cst.Attribute):
            if hasattr(node.func.value, "value") and hasattr(node.func.attr, "value"):
                self._calls.append(((node.func.value.value, node.func.attr.value), self._ranges[node]))
