import ast

def parse_python(python: str, context: dict) -> dict[str, list]:
    global_env = dict(context)
    local_env = {}

    code = compile(python, "_temp_", "exec")
    exec(code, global_env, local_env)

    values = {key: value for key, value in global_env if key not in context}
    values.update(local_env)
