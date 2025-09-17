import requests
import json

OPENAPI_URL = "http://localhost:8003/openapi.json"

def resolve_ref(ref, components):
    # ref is like "#/components/schemas/TransactionCreate"
    parts = ref.lstrip("#/").split("/")
    obj = components
    for part in parts[1:]:
        obj = obj[part]
    return obj

def get_example_value(schema, components):
    if "$ref" in schema:
        schema = resolve_ref(schema["$ref"], components)
    t = schema.get("type")
    if "enum" in schema:
        return schema["enum"][0]
    if t == "string":
        fmt = schema.get("format")
        if fmt == "uuid":
            return "00000000-0000-0000-0000-000000000000"
        if fmt == "date":
            return "2024-01-01"
        return "example-string"
    if t == "integer":
        return 123
    if t == "number":
        return 1.23
    if t == "boolean":
        return True
    if t == "array":
        return [get_example_value(schema["items"], components)]
    if t == "object":
        return {k: get_example_value(v, components) for k, v in schema.get("properties", {}).items()}
    return "example"

def main():
    resp = requests.get(OPENAPI_URL)
    openapi = resp.json()
    paths = openapi["paths"]
    components = openapi.get("components", {})
    for path, methods in paths.items():
        for method, details in methods.items():
            url = f"http://localhost:8003{path}"
            # Handle path parameters
            if "parameters" in details:
                for param in details["parameters"]:
                    if param["in"] == "path":
                        schema = param.get("schema", {})
                        example = get_example_value(schema, components)
                        url = url.replace("{" + param["name"] + "}", str(example))
            # Handle query parameters
            params = []
            if "parameters" in details:
                for param in details["parameters"]:
                    if param["in"] == "query":
                        schema = param.get("schema", {})
                        example = get_example_value(schema, components)
                        params.append(f"{param['name']}={example}")
            if params:
                url = f"{url}?{'&'.join(params)}"
            cmd = f"curl -X {method.upper()} '{url}'"
            # Add body
            if "requestBody" in details:
                content = details["requestBody"]["content"]
                if "application/json" in content:
                    schema = content["application/json"]["schema"]
                    example = get_example_value(schema, components)
                    cmd += f" -H 'Content-Type: application/json' -d '{json.dumps(example)}'"
            print(cmd)

if __name__ == "__main__":
    main()