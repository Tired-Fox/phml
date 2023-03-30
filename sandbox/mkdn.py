import ast
from typing import Any, Collection

RESULT = "_phml_embedded_result_"
def update_ast_node_pos(dest, source):
    """Assign lineno, end_lineno, col_offset, and end_col_offset
    from a source python ast node to a destination python ast node.
    """
    dest.lineno = source.lineno
    dest.end_lineno = source.end_lineno
    dest.col_offset = source.col_offset
    dest.end_col_offset = source.end_col_offset

def exec_embedded(code: str, **context) -> Any:
    AST = ast.parse(code)
    last = AST.body[-1]
    returns = [ret for ret in AST.body if isinstance(ret, ast.Return)]

    if len(returns) > 0:
        last = returns[0]
        idx = AST.body.index(last)

        n_expr = ast.Name(id=RESULT, ctx=ast.Store())
        n_assign = ast.Assign(targets=[n_expr], value=last.value)

        update_ast_node_pos(dest=n_expr, source=last)
        update_ast_node_pos(dest=n_assign, source=last)

        AST.body = [*AST.body[:idx], n_assign]
    elif isinstance(last, ast.Expr):
        n_expr = ast.Name(id=RESULT, ctx=ast.Store())
        n_assign = ast.Assign(targets=[n_expr], value=last.value)

        update_ast_node_pos(dest=n_expr, source=last)
        update_ast_node_pos(dest=n_assign, source=last)

        AST.body[-1] = n_assign
    elif isinstance(last, ast.Assign):
        n_expr = ast.Name(id=RESULT, ctx=ast.Store())
        update_ast_node_pos(dest=n_expr, source=last)
        last.targets.append(n_expr)

    ccode = compile(AST, "_phml_embedded_", "exec")
    local_env = {}
    exec(ccode, {**context}, local_env)
    return local_env[RESULT]

def blank(collection: Collection) -> bool:
    if collection is None or not hasattr(collection, "__len__"):
        return True
    return len(collection) == 0

if __name__ == "__main__":
    data = {'monday': 'MONDAY', 'tuesday': 'TUESDAY'}
    code = """
data['monday']
result = data['tuesday']
"""
    result = exec_embedded(
        code,
        data=data,
        blank=blank
    )
    print(result)
