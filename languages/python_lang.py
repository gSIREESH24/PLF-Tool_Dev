def run(code, context):
    # Define export function inside Python block
    def export(name, value):
        context.set(name, value)

    # Inject export and context variables
    local_env = context.all().copy()
    local_env["export"] = export

    exec(code, local_env)

    # Update context with new variables
    for key, value in local_env.items():
        if not key.startswith("__") and key != "export":
            context.set(key, value)
