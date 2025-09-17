import os
import random
import subprocess
from datetime import date, datetime, timezone
from uuid import uuid4
from jinja2 import Environment, FileSystemLoader
import json
from tables import get_tables

TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'template_for_db_tables'))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
OUTPUT_BASE_DIR = os.path.join(PROJECT_ROOT, 'services', 'db')
def remove_legacy_output_dir():
    legacy_output = os.path.join(os.path.dirname(__file__), 'output')
    if os.path.exists(legacy_output):
        import shutil
        print(f"[INFO] Removing legacy output directory: {legacy_output}")
        shutil.rmtree(legacy_output)
BRUNO_BASE_DIR = "bruno/microservices"

def make_test_value(field):
    t = field["pydantic_type"]
    if field["name"] == "workspace_id":
        return "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"  # Always use a fixed UUID for test workspace
    if t == "int":
        return random.randint(1, 10000)
    elif t == "float":
        return round(random.uniform(-180, 180), 6)
    elif t == "str":
        return f"test_{field['name']}"
    elif t == "datetime":
        return datetime.now(timezone.utc).isoformat()
    elif t == "date":
        return date.today().isoformat()
    elif t == "UUID":
        return "00000000-0000-0000-0000-000000000001"
    elif "enum_type" in field:
        return get_enum_member(field["enum_type"])
    else:
        return f"unknown_{field['name']}"

def get_enum_member(enum_name):
    mapping = {
        "LocationType": "HQ",
        "CountryCode": "USA",
        "USState": "CA",
        "TransactionPhase": "PRE_LISTING",
        "TransactionStatus": "ACTIVE",
        "ConversationType": "thread",
        "CommunicationEventType": "email",
        "CommunicationStatus": "sent"
    }
    return mapping.get(enum_name, "UNKNOWN")

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    keep_trailing_newline=True,
    autoescape=False
)
env.globals["make_test_value"] = make_test_value
env.filters["repr"] = repr

def render_for_table(table_name: str, config: dict):
    print(f"[DEBUG] Entering render_for_table for: {table_name}, output_dir: {os.path.join(OUTPUT_BASE_DIR, table_name)}")
    print(f"[TRACE] render_for_table START: {table_name}")
    output_dir = os.path.join(OUTPUT_BASE_DIR, table_name)
    print(f"[TRACE] output_dir resolved: {output_dir}")
    # --- ENFORCE BUSINESS RULES ---
    # Remove deprecated user_id field
    fields = [f for f in config["fields"] if f["name"] != "user_id"]
    print(f"[TRACE] fields after user_id removal: {fields}")

    # Ensure workspace_id is present and required
    if not any(f["name"] == "workspace_id" for f in fields):
        fields.append({
            "name": "workspace_id",
            "required": True,
            "sqlalchemy_type": "UUID",
            "pydantic_type": "UUID"
        })
    else:
        for f in fields:
            if f["name"] == "workspace_id":
                f["required"] = True
    print(f"[TRACE] fields after workspace_id enforcement: {fields}")

    # Ensure created_by is present and required for new records (skip for lookup/reference tables if needed)
    if table_name not in ["lookup", "reference"]:  # adjust as needed
        if not any(f["name"] == "created_by" for f in fields):
            fields.append({
                "name": "created_by",
                "required": True,
                "sqlalchemy_type": "UUID",
                "pydantic_type": "UUID"
            })
        else:
            for f in fields:
                if f["name"] == "created_by":
                    f["required"] = True
    print(f"[TRACE] fields after created_by enforcement: {fields}")

    enum_fields = [f for f in fields if f.get("enum_type")]
    enum_imports = list({f["enum_type"] for f in enum_fields})
    print(f"[TRACE] enum_fields: {enum_fields}, enum_imports: {enum_imports}")

    for root, dirs, files in os.walk(TEMPLATE_DIR):
        print(f"[TRACE] os.walk root: {root}, dirs: {dirs}, files: {files}")
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"venv", "__pycache__"}]
        for file in files:
            print(f"[TRACE] Considering file: {file}")
            if not file.endswith(".j2"):
                print(f"[TRACE] Skipping non-template file: {file}")
                continue
            rel_dir = os.path.relpath(root, TEMPLATE_DIR)
            stripped_name = file[:-3]
            if rel_dir.endswith("models") and stripped_name == "model.py":
                stripped_name = f"{table_name}.py"
            elif rel_dir.endswith("schemas") and stripped_name == "schema.py":
                stripped_name = f"{table_name}.py"
            elif rel_dir.endswith("use_cases"):
                for prefix in ["create_", "delete_", "get_", "search_", "update_"]:
                    if stripped_name.startswith(prefix):
                        stripped_name = f"{prefix}{table_name}.py"
                        break
            rel_path = os.path.join("" if rel_dir == "." else rel_dir, stripped_name)
            src_template_path = os.path.join(rel_dir, file)
            dst_path = os.path.join(output_dir, rel_path)
            print(f"[TRACE] Template: {src_template_path} -> Output: {dst_path}")
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            try:
                template = env.get_template(src_template_path)
                rendered = template.render(
                    table_name=table_name,
                    port=config["port"],
                    fields=fields,  # use the filtered/augmented fields
                    enum_fields=enum_fields,
                    enum_imports=enum_imports
                )
                print(f"[TRACE] Writing file: {dst_path}")
                with open(dst_path, "w") as f:
                    f.write(rendered)
                print(f"[TRACE] Successfully wrote: {dst_path}")
            except Exception as e:
                print(f"[ERROR] Failed to render {src_template_path}: {e}")
                import traceback
                traceback.print_exc()
                raise
    print(f"[TRACE] render_for_table END: {table_name}")

def render_all_tables():
    print(f"[TRACE] render_all_tables START")
    tables = get_tables()
    print(f"[TRACE] Tables to render: {list(tables.keys())}")
    for table, cfg in tables.items():
        print(f"[TRACE] Rendering: {table}")
        render_for_table(table, cfg)
    print("[TRACE] render_all_tables END")


def cleanup_removed_microservices():
    print("[INFO] Cleaning up removed microservices...")
    defined_tables = set(get_tables().keys())
    for subdir in os.listdir(OUTPUT_BASE_DIR):
        if subdir not in defined_tables:
            service_dir = os.path.join(OUTPUT_BASE_DIR, subdir)
            compose_file = os.path.join(service_dir, "docker-compose.yml")
            if os.path.isdir(service_dir) and os.path.exists(compose_file):
                try:
                    subprocess.run(
                        ["docker", "compose", "down", "--remove-orphans", "--volumes"],
                        cwd=service_dir,
                        check=True,
                        env=os.environ
                    )
                except Exception as e:
                    print(f"[WARN] Could not stop/remove containers in {service_dir}: {e}")
            try:
                import shutil
                shutil.rmtree(service_dir)
                print(f"[INFO] Removed directory: {service_dir}")
            except Exception as e:
                print(f"[WARN] Could not remove directory {service_dir}: {e}")

def generate_bruno_folder_structure():
    """
    Ensures the Bruno directory structure exists and writes folder.bru meta files for each folder,
    and writes the root bruno.json collection file.
    """
    BRUNO_API_ROOT = "bruno/API"
    BRUNO_MICROSERVICES_DIR = os.path.join(BRUNO_API_ROOT, "Microservices")
    os.makedirs(BRUNO_MICROSERVICES_DIR, exist_ok=True)

    # Write the root bruno.json
    bruno_json_path = os.path.join(BRUNO_API_ROOT, "bruno.json")
    bruno_json_content = {
        "version": "1",
        "name": "Parent",
        "type": "collection",
        "ignore": [
            "node_modules",
            ".git"
        ]
    }
    with open(bruno_json_path, "w") as f:
        import json
        json.dump(bruno_json_content, f, indent=2)

    # Write the Microservices folder.bru
    with open(os.path.join(BRUNO_MICROSERVICES_DIR, "folder.bru"), "w") as f:
        f.write("meta {\n  name: Microservices\n}\n")

    tables = get_tables()
    for table in tables:
        service_dir = os.path.join(BRUNO_MICROSERVICES_DIR, table.capitalize())
        os.makedirs(service_dir, exist_ok=True)
        # Write the service folder.bru
        with open(os.path.join(service_dir, "folder.bru"), "w") as f:
            f.write(f"meta {{\n  name: {table.capitalize()}\n}}\n")

def generate_bruno_requests():
    """
    Generates CRUD .bru request files for each microservice in the Bruno structure.
    """
    BRUNO_API_ROOT = "bruno/API"
    BRUNO_MICROSERVICES_DIR = os.path.join(BRUNO_API_ROOT, "Microservices")
    tables = get_tables()
    for table, cfg in tables.items():
        port = cfg["port"]
        service_dir = os.path.join(BRUNO_MICROSERVICES_DIR, table.capitalize())
        id_field = next((f for f in cfg["fields"] if f.get("primary_key")), None)
        id_value = "00000000-0000-0000-0000-000000000001" if id_field and id_field["pydantic_type"] == "UUID" else "1"

        # --- Create ---
        create_body = {}
        for field in cfg["fields"]:
            if not field.get("primary_key") and field.get("required", False):
                create_body[field["name"]] = make_test_value(field)
        with open(os.path.join(service_dir, "Create.bru"), "w") as f:
            f.write(f"""meta {{
  name: Create
  type: http
  seq: 1
}}

post {{
  url: http://localhost:{port}/
  body: json
  auth: inherit
}}

body:json {{
{json.dumps(create_body, indent=2)}
}}
""")

        # --- List ---
        with open(os.path.join(service_dir, "List.bru"), "w") as f:
            f.write(f"""meta {{
  name: List
  type: http
  seq: 2
}}

get {{
  url: http://localhost:{port}/
  body: none
  auth: inherit
}}
""")

        # --- Get one ---
        with open(os.path.join(service_dir, "Get one.bru"), "w") as f:
            f.write(f"""meta {{
  name: Get one
  type: http
  seq: 3
}}

get {{
  url: http://localhost:{port}/{id_value}
  body: none
  auth: inherit
}}
""")

        # --- Update ---
        update_body = create_body.copy()
        # Mutate one field for update
        for k, v in update_body.items():
            if isinstance(v, str):
                update_body[k] = v + "_updated"
                break
        with open(os.path.join(service_dir, "Update.bru"), "w") as f:
            f.write(f"""meta {{
  name: Update
  type: http
  seq: 4
}}

put {{
  url: http://localhost:{port}/{id_value}
  body: json
  auth: inherit
}}

body:json {{
{json.dumps(update_body, indent=2)}
}}
""")

        # --- Delete ---
        with open(os.path.join(service_dir, "Delete.bru"), "w") as f:
            f.write(f"""meta {{
  name: Delete
  type: http
  seq: 5
}}

delete {{
  url: http://localhost:{port}/{id_value}
  body: none
  auth: inherit
}}
""")

# Call this function in orchestrate() if you want it to always run:
def orchestrate():
    print(f"[TRACE] orchestrate START")
    print(f"[TRACE] Current working directory: {os.getcwd()}")
    print(f"[TRACE] Output base directory: {OUTPUT_BASE_DIR}")
    remove_legacy_output_dir()
    cleanup_removed_microservices()
    render_all_tables()
    generate_bruno_folder_structure()
    generate_bruno_requests()  # <-- Add this line
    print(f"[TRACE] orchestrate END")
    print(f"[TRACE] orchestrate END")


if __name__ == "__main__":
    orchestrate()
