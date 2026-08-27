"""Safe Abstract Syntax Tree (AST) Business Rule Parser and Evaluator.

Allows risk officers to author flexible, declarative boolean expressions:
e.g. `amount > 2500 AND (velocity_1h > 3 OR country_code != 'US')`
Evaluates safely in sub-millisecond time without using unsafe Python `eval()`.
"""

from __future__ import annotations
import ast
import operator
import re
from typing import Dict, Any, Optional, Tuple, Set


class SafeRuleEvaluator:
    """AST-based safe logical and numerical rule engine."""

    # Supported binary and comparison operators
    _BINARY_OPS = {
        ast.And: lambda left, right: left and right,
        ast.Or: lambda left, right: left or right,
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    _CMP_OPS = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.In: lambda a, b: a in b,
        ast.NotIn: lambda a, b: a not in b,
    }

    @classmethod
    def evaluate_expression(cls, expression: str, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Parse and evaluate boolean expression string against context dictionary."""
        # Normalize expression (replace keywords like AND, OR, NOT with python syntax and, or, not)
        clean_expr = cls._normalize_expression(expression)

        try:
            tree = ast.parse(clean_expr, mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Rule syntax error in '{expression}': {str(e)}")

        matched_vars: Dict[str, Any] = {}
        result = cls._eval_node(tree.body, context, matched_vars)
        return bool(result), matched_vars

    @classmethod
    def _normalize_expression(cls, expr: str) -> str:
        """Replace SQL / DSL operators with Python equivalents."""
        s = expr
        # Replace word boundary boolean operators
        s = re.sub(r"\bAND\b", "and", s, flags=re.IGNORECASE)
        s = re.sub(r"\bOR\b", "or", s, flags=re.IGNORECASE)
        s = re.sub(r"\bNOT\b", "not", s, flags=re.IGNORECASE)
        s = re.sub(r"\bNULL\b", "None", s, flags=re.IGNORECASE)
        s = re.sub(r"\bTRUE\b", "True", s, flags=re.IGNORECASE)
        s = re.sub(r"\bFALSE\b", "False", s, flags=re.IGNORECASE)
        s = re.sub(r"=", "==", s)
        s = re.sub(r"====|====", "==", s)
        s = re.sub(r"!==|!=", "!=", s)
        s = re.sub(r"<==", "<=", s)
        s = re.sub(r">==", ">=", s)
        return s

    @classmethod
    def _eval_node(cls, node: ast.AST, context: Dict[str, Any], matched_vars: Dict[str, Any]) -> Any:
        """Recursively evaluate AST nodes safely."""
        if isinstance(node, ast.Constant):  # Python 3.8+ literal
            return node.value

        elif isinstance(node, ast.Name):
            var_name = node.id
            val = context.get(var_name, None)
            matched_vars[var_name] = val
            return val

        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return not cls._eval_node(node.operand, context, matched_vars)
            elif isinstance(node.op, ast.USub):
                return -cls._eval_node(node.operand, context, matched_vars)

        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                for val_node in node.values:
                    res = cls._eval_node(val_node, context, matched_vars)
                    if not res:
                        return False
                return True
            elif isinstance(node.op, ast.Or):
                for val_node in node.values:
                    res = cls._eval_node(val_node, context, matched_vars)
                    if res:
                        return True
                return False

        elif isinstance(node, ast.BinOp):
            left = cls._eval_node(node.left, context, matched_vars)
            right = cls._eval_node(node.right, context, matched_vars)
            op_type = type(node.op)
            if op_type in cls._BINARY_OPS:
                return cls._BINARY_OPS[op_type](left, right)

        elif isinstance(node, ast.Compare):
            left = cls._eval_node(node.left, context, matched_vars)
            for op, comparator in zip(node.ops, node.comparators):
                right = cls._eval_node(comparator, context, matched_vars)
                op_type = type(op)
                if op_type in cls._CMP_OPS:
                    if not cls._cmp_safe(left, right, op_type):
                        return False
                    left = right
                else:
                    return False
            return True

        elif isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return [cls._eval_node(elt, context, matched_vars) for elt in node.elts]

        raise ValueError(f"Unsupported AST expression element: {type(node).__name__}")

    @classmethod
    def _cmp_safe(cls, left: Any, right: Any, op_type: Any) -> bool:
        """Perform type-coerced safe comparison."""
        if left is None or right is None:
            if op_type == ast.Eq:
                return left == right
            elif op_type == ast.NotEq:
                return left != right
            return False

        # Numeric type coercion (e.g. float vs int)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            left = float(left)
            right = float(right)

        return cls._CMP_OPS[op_type](left, right)
