import re
from typing import Optional, Any, List, Union, Tuple
import os
import json
import requests
import csv
from optics_framework.common.logging_config import logger
from optics_framework.common.runner.test_runnner import TestRunner
import ast
from functools import wraps


def raw_params(*indices):
    """Decorator to mark parameter indices that should remain unresolved."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper._raw_param_indices = indices
        return wrapper
    return decorator


class FlowControl:
    def __init__(self, runner: TestRunner | None):
        self.runner: TestRunner | None = runner

    def _ensure_runner(self):
        if self.runner is None:
            raise Exception(
                "FlowControl.runner is not set. Please assign a valid runner instance before using FlowControl.")

    def execute_module(self, module_name: str) -> List[Any]:
        self._ensure_runner()
        if module_name not in self.runner.modules:
            raise ValueError(f"Module '{module_name}' not found.")

        results = []
        for keyword, params in self.runner.modules[module_name]:
            try:
                resolved_params = [self.runner.resolve_param(
                    param) for param in params]
            except Exception as e:
                raise ValueError(
                    f"Parameter resolution failed in module '{module_name}': {e}")
            func_name = "_".join(keyword.split()).lower()
            method = self.runner.keyword_map.get(func_name)
            if method is None:
                raise ValueError(
                    f"Keyword '{keyword}' not found in module '{module_name}'.")
            result = method(*resolved_params)
            results.append(result)
        return results

    @raw_params(1, 3, 5, 7, 9, 11, 13, 15)
    def run_loop(self, target: str, *args: str) -> List[Any]:
        self._ensure_runner()
        if len(args) == 1:
            return self._loop_by_count(target, args[0])
        return self._loop_with_variables(target, args)

    def _loop_by_count(self, target: str, count_str: str) -> List[Any]:
        try:
            iterations = int(count_str)
            if iterations < 1:
                raise ValueError("Iteration count must be at least 1.")
        except ValueError as e:
            if str(e) == "Iteration count must be at least 1.":
                raise
            raise ValueError(
                f"Expected an integer for loop count, got '{count_str}'.")

        results = []
        for i in range(iterations):
            logger.debug(
                f"[RUN LOOP] Iteration {i+1}: Executing target '{target}'")
            result = self.execute_module(target)
            results.append(result)
        return results

    def _loop_with_variables(self, target: str, args: Tuple[str, ...]) -> List[Any]:
        if len(args) % 2 != 0:
            raise ValueError(
                "Expected an even number of arguments for variable-iterable pairs.")

        variables = args[0::2]
        iterables = args[1::2]
        var_names, parsed_iterables = self._parse_variable_iterable_pairs(
            variables, iterables)
        min_length = min(len(lst) for lst in parsed_iterables)
        if not isinstance(self.runner.elements, dict):
            self.runner.elements = {}

        results = []
        for i in range(min_length):
            for var_name, iterable_values in zip(var_names, parsed_iterables):
                value = iterable_values[i]
                logger.debug(
                    f"[RUN LOOP] Iteration {i+1}: Setting {var_name} = {value}")
                self.runner.elements[var_name] = value
            logger.debug(
                f"[RUN LOOP] Iteration {i+1}: Executing target '{target}'")
            result = self.execute_module(target)
            results.append(result)
        return results

    def _parse_variable_iterable_pairs(self, variables: Tuple[str, ...], iterables: Tuple[str, ...]) -> Tuple[List[str], List[List[Any]]]:
        """Parse variable names and their corresponding iterables."""
        var_names = self._parse_variable_names(variables)
        parsed_iterables = self._parse_iterables(variables, iterables)
        return var_names, parsed_iterables

    def _parse_variable_names(self, variables: Tuple[str, ...]) -> List[str]:
        """Extract and clean variable names from the input tuple."""
        var_names = []
        for variable in variables:
            var_name = variable.strip()
            if var_name.startswith("${") and var_name.endswith("}"):
                var_name = var_name[2:-1].strip()
            else:
                logger.warning(
                    f"[RUN LOOP] Expected variable in format '${{name}}', got '{variable}'. Using as is.")
            var_names.append(var_name)
        return var_names

    def _parse_iterables(self, variables: Tuple[str, ...], iterables: Tuple[str, ...]) -> List[List[Any]]:
        """Parse iterables into lists, handling JSON strings and validating input."""
        parsed_iterables = []
        for i, iterable in enumerate(iterables):
            parsed = self._parse_single_iterable(iterable, variables[i])
            if not parsed:
                raise ValueError(
                    f"Iterable for variable '{variables[i]}' is empty.")
            parsed_iterables.append(parsed)
        return parsed_iterables

    def _parse_single_iterable(self, iterable: Any, variable: str) -> List[Any]:
        """Parse a single iterable, converting JSON strings or validating lists."""
        if isinstance(iterable, str):
            try:
                values = json.loads(iterable)
                if not isinstance(values, list):
                    raise ValueError(
                        f"Iterable '{iterable}' for variable '{variable}' must resolve to a list.")
                return values
            except json.JSONDecodeError:
                raise ValueError(
                    f"Invalid iterable format for variable '{variable}': '{iterable}'.")
        elif isinstance(iterable, list):
            return iterable
        else:
            raise ValueError(
                f"Expected a list or JSON string for iterable of variable '{variable}', got {type(iterable).__name__}.")

    def condition(self, *args) -> Optional[List[Any]]:
        self._ensure_runner()
        if not args:
            raise ValueError("No condition-target pairs provided.")
        pairs, else_target = self._split_condition_args(args)
        return self._evaluate_conditions(pairs, else_target)

    def _split_condition_args(self, args: Tuple[str, ...]) -> Tuple[List[Tuple[str, str]], Optional[str]]:
        pairs = []
        else_target = None
        if len(args) % 2 == 1:
            for i in range(0, len(args) - 1, 2):
                pairs.append((args[i], args[i + 1]))
            else_target = args[-1]
        else:
            for i in range(0, len(args), 2):
                pairs.append((args[i], args[i + 1]))
        return pairs, else_target

    def _evaluate_conditions(self, pairs: List[Tuple[str, str]], else_target: Optional[str]) -> Optional[List[Any]]:
        for cond, target in pairs:
            cond_str = cond.strip()
            if not cond_str:
                continue
            if self._is_condition_true(cond_str):
                logger.debug(
                    f"[CONDITION] Condition '{cond_str}' is True. Executing target '{target}'.")
                return self.execute_module(target)
            logger.debug(f"[CONDITION] Condition '{cond_str}' is False.")
        if else_target is not None:
            logger.debug(
                f"[CONDITION] No condition met. Executing ELSE target '{else_target}'.")
            return self.execute_module(else_target)
        return None

    def _is_condition_true(self, cond: str) -> bool:
        try:
            resolved_cond = self._resolve_condition(cond)
            return bool(self._safe_eval(resolved_cond))
        except Exception as e:
            raise ValueError(f"Error evaluating condition '{cond}': {e}")

    def _resolve_condition(self, cond: str) -> str:
        pattern = re.compile(r"\$\{([^}]+)\}")

        def replacer(match):
            var_name = match.group(1).strip()
            value = self.runner.elements.get(var_name)
            if value is None:
                raise ValueError(
                    f"Variable '{var_name}' not found for condition resolution.")
            try:
                float(value)
                return value
            except ValueError:
                return f"'{value}'"
        return pattern.sub(replacer, cond)

    @raw_params(0)
    def read_data(self, input_element: str, file_path: Union[str, List[Any]], index: Optional[int] = None):
        self._ensure_runner()
        elem_name = self._extract_element_name(input_element)
        data = self._load_data(file_path, index)
        if not isinstance(self.runner.elements, dict):
            self.runner.elements = {}
        self.runner.elements[elem_name] = data
        return data

    def _extract_element_name(self, input_element: str) -> str:
        elem_name = input_element.strip()
        if elem_name.startswith("${") and elem_name.endswith("}"):
            return elem_name[2:-1].strip()
        logger.warning(
            f"[READ DATA] Expected element in format '${{name}}', got '{input_element}'. Using as is.")
        return elem_name

    def _load_data(self, file_path: Union[str, List[Any]], index: Optional[int]) -> List[Any]:
        # Direct list input
        if isinstance(file_path, list):
            return file_path

        # API call
        elif file_path.lower().startswith("http"):
            try:
                response = requests.get(file_path, timeout=(5, 30))
                if response.status_code != 200:
                    raise ValueError(
                        f"Failed to fetch data from API: {file_path}")
                json_data = response.json()

                if not isinstance(json_data, list):
                    raise ValueError("API response must be a JSON list.")

                if not isinstance(index, str):
                    raise ValueError(
                        "For API data, 'index' must be a string (JSON key).")

                extracted_data = [item[index]
                                  for item in json_data if index in item]
                return extracted_data
            except requests.Timeout:
                raise ValueError(f"Request to {file_path} timed out.")
            except requests.RequestException as e:
                raise ValueError(f"Failed to fetch data from {file_path}: {e}")

        # File input (only CSV supported)
        else:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File '{file_path}' not found.")

            file_extension = os.path.splitext(file_path)[-1].lower()

            if file_extension == '.csv':
                with open(file_path, newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    data = list(reader)
                    if not data:
                        raise ValueError(f"CSV file '{file_path}' is empty.")
                    # Assume first row is headers if index is a string
                    if isinstance(index, str):
                        headers = data[0]
                        if index not in headers:
                            raise ValueError(
                                f"Column '{index}' not found in CSV file.")
                        col_idx = headers.index(index)
                        return [row[col_idx] for row in data[1:] if row[col_idx]]
                    elif isinstance(index, int):
                        if index >= len(data[0]):
                            raise IndexError("Index out of range.")
                        return [row[index] for row in data[1:] if row[index]]
                    elif index is None:
                        return [row[0] for row in data[1:] if row[0]]
                    else:
                        raise ValueError(
                            "Index must be a string (column name) or an integer (column index).")
            else:
                raise ValueError(
                    "Unsupported file format. Use CSV or provide a list/URL.")

    @raw_params(0)
    def evaluate(self, param1: str, param2: str):
        self._ensure_runner()
        var_name = self._extract_variable_name(param1)
        result = self._compute_expression(param2)
        self.runner.elements[var_name] = str(result)
        return result

    def _extract_variable_name(self, param1: str) -> str:
        var_name = param1.strip()
        if var_name.startswith("${") and var_name.endswith("}"):
            return var_name[2:-1].strip()
        logger.warning(
            f"[EVALUATE] Expected param1 in format '${{name}}', got '{param1}'. Using as is.")
        return var_name

    def _compute_expression(self, param2: str) -> Any:
        def replace_var(match):
            var_name = match.group(1)
            if var_name not in self.runner.elements:
                raise ValueError(
                    f"Variable '{var_name}' not found in elements.")
            return str(self.runner.elements[var_name])
        param2_resolved = re.sub(r"\$\{([^}]+)\}", replace_var, param2)
        return self._safe_eval(param2_resolved)

    def _safe_eval(self, expression: str) -> Any:
        try:
            node = ast.parse(expression, mode='eval')
            allowed_nodes = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
                             ast.IfExp, ast.NameConstant, ast.Constant, ast.Load,
                             ast.Num, ast.Str, ast.List, ast.Tuple)
            allowed_operators = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod,
                                 ast.Pow, ast.Lt, ast.Gt, ast.Eq, ast.NotEq,
                                 ast.LtE, ast.GtE, ast.And, ast.Or, ast.Not)
            for node in ast.walk(node):
                if not isinstance(node, allowed_nodes) and not isinstance(node, allowed_operators):
                    raise ValueError(
                        f"Unsafe expression detected: {expression}")
            return eval(expression, {"__builtins__": None}, {}) # nosec
        except Exception as e:
            raise ValueError(
                f"Error evaluating expression '{expression}': {e}")
