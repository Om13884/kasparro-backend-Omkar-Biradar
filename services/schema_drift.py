def extract_schema_signature(payload: dict) -> dict:
    """
    Extract a lightweight schema signature from JSON payload.
    Only top-level keys and value types.
    """
    signature = {}

    for key, value in payload.items():
        signature[key] = type(value).__name__

    return signature


def diff_schemas(old: dict, new: dict) -> dict:
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))

    type_changes = {
        k: {"old": old[k], "new": new[k]}
        for k in old.keys() & new.keys()
        if old[k] != new[k]
    }

    return {
        "added_fields": added,
        "removed_fields": removed,
        "type_changes": type_changes,
        "change_score": len(added) + len(removed) + len(type_changes),
    }
