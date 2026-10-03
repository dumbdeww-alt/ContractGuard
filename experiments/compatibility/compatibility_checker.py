import json


def load_schema(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def check_compatibility(old_schema, new_schema):
    old_properties = old_schema["properties"]
    new_properties = new_schema["properties"]

    old_required = set(old_schema.get("required", []))
    new_required = set(new_schema.get("required", []))

    changes = []

    # Check removed fields
    for field in old_properties:
        if field not in new_properties:
            if field in old_required:
                changes.append(f"BREAKING: Required field '{field}' was removed.")
            else:
                changes.append(f"WARNING: Optional field '{field}' was removed.")

    # Check type changes
    for field in old_properties:
        if field in new_properties:
            old_type = old_properties[field]["type"]
            new_type = new_properties[field]["type"]

            if old_type != new_type:
                changes.append(
                    f"BREAKING: Field '{field}' changed from "
                    f"{old_type} to {new_type}."
                )

    # Check newly required fields
    for field in new_required:
        if field not in old_required:
            changes.append(f"BREAKING: Field '{field}' is now required.")

    if not changes:
        return "COMPATIBLE"

    return "\n".join(changes)


if __name__ == "__main__":
    old_schema = load_schema("../../sample-data/versions/student_contract_v1.json")
    new_schema = load_schema("../../sample-data/versions/student_contract_v2_compatible.json")

    result = check_compatibility(old_schema, new_schema)

    print("Compatibility Result:")
    print(result)
