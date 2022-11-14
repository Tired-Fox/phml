data = {
    "name": "Zachary",
    "age": "22"
}

# Pass data into locals
local_env = {"data": data}
# Execute with locals
exec("phml_vp_result = data['name']", {}, local_env)

# Extract result
print(local_env["phml_vp_result"])