#!/usr/bin/env python3
"""Validate samples.json against the JSON schema."""

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "jsonschema"])
    import jsonschema


def main():
    root = Path(__file__).resolve().parent.parent
    schema_path = root / "dataset" / "schema.json"
    samples_path = root / "dataset" / "annotations" / "samples.json"

    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    with open(samples_path, encoding="utf-8") as f:
        data = json.load(f)

    samples = data.get("samples", data) if isinstance(data, dict) else data

    validator = jsonschema.Draft7Validator(schema)
    violations = []

    for i, sample in enumerate(samples):
        errors = list(validator.iter_errors(sample))
        for err in errors:
            path = ".".join(str(p) for p in err.absolute_path) or "(root)"
            violations.append(f"  [{sample.get('task_id', i)}] {path}: {err.message}")

    if violations:
        print(f"FAIL — {len(violations)} violation(s) found:\n")
        for v in violations:
            print(v)
        sys.exit(1)
    else:
        print(f"PASS — {len(samples)} sample(s) validated, zero errors.")
        sys.exit(0)


if __name__ == "__main__":
    main()
