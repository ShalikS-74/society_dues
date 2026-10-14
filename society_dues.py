"""Manage apartment-society maintenance dues and late fees."""

import ast
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE dues (flat TEXT, month TEXT, amount INTEGER, paid INTEGER)"
)


def add_due(flat, month, amount, history=None):
    """Add an unpaid due and return the supplied call history."""
    if history is None:
        history = []

    conn.execute(
        "INSERT INTO dues (flat, month, amount, paid) VALUES (?, ?, ?, ?)",
        (flat, month, amount, 0),
    )
    history.append((flat, month))
    return history


def collect(flat, month):
    """Mark a due as paid and return its amount, or None when it is absent."""
    row = conn.execute(
        "SELECT amount FROM dues WHERE flat = ? AND month = ?", (flat, month)
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE dues SET paid = 1 WHERE flat = ? AND month = ?",
            (flat, month),
        )
        return row[0]
    return None


def evaluate_arithmetic(expression):
    """Evaluate numeric arithmetic without executing Python code."""
    if isinstance(expression, ast.Constant):
        if type(expression.value) in (int, float):
            return expression.value
        raise ValueError("Only numeric values are allowed")

    if isinstance(expression, ast.UnaryOp) and isinstance(
        expression.op, (ast.UAdd, ast.USub)
    ):
        value = evaluate_arithmetic(expression.operand)
        return value if isinstance(expression.op, ast.UAdd) else -value

    if isinstance(expression, ast.BinOp):
        left = evaluate_arithmetic(expression.left)
        right = evaluate_arithmetic(expression.right)
        operators = {
            ast.Add: lambda: left + right,
            ast.Sub: lambda: left - right,
            ast.Mult: lambda: left * right,
            ast.Div: lambda: left / right,
            ast.FloorDiv: lambda: left // right,
            ast.Mod: lambda: left % right,
        }
        operation = operators.get(type(expression.op))
        if operation:
            return operation()

    raise ValueError("Only basic arithmetic is allowed")


def penalty(rule):
    """Return the late fee for a valid arithmetic rule, otherwise zero."""
    try:
        parsed_rule = ast.parse(rule, mode="eval")
        late_fee = evaluate_arithmetic(parsed_rule.body)
    except (SyntaxError, TypeError, ValueError, ZeroDivisionError):
        late_fee = 0
    return late_fee


def pending():
    """Return the flat numbers that still have unpaid dues."""
    rows = conn.execute("SELECT flat FROM dues WHERE paid = 0").fetchall()
    return [row[0] for row in rows]


def main():
    """Run a short demonstration of the dues ledger."""
    add_due("A-101", "Oct", 2500)
    add_due("A-102", "Oct", 2500)
    print(collect("A-101", "Oct"))
    print(penalty("50 * 2"))
    print(pending())


if __name__ == "__main__":
    main()
