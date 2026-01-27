import ast
import operator
import math


class SafeCalculator:
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    functions = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log10,
        "sqrt": math.sqrt,
        "pi": lambda: math.pi
    }

    def evaluate(self, expression: str):
        try:
            node = ast.parse(expression, mode="eval")
            return self._eval(node.body)
        except Exception:
            raise ValueError("Invalid Expression")

    def _eval(self, node):
        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.BinOp):
            return self.operators[type(node.op)](
                self._eval(node.left),
                self._eval(node.right)
            )

        if isinstance(node, ast.UnaryOp):
            return self.operators[type(node.op)](
                self._eval(node.operand)
            )

        if isinstance(node, ast.Call):
            func_name = node.func.id
            if func_name not in self.functions:
                raise ValueError("Unsupported function")
            args = [self._eval(arg) for arg in node.args]
            return self.functions[func_name](*args)

        if isinstance(node, ast.Name):
            if node.id == "pi":
                return math.pi

        raise ValueError("Invalid syntax")
