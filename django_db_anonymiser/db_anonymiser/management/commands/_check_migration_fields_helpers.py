import re
import shlex
import subprocess  # nosec B404

import yaml


def get_diff_content():
    result = subprocess.run(  # nosec B603
        shlex.split("git diff --cached --name-only"),
        capture_output=True,
        text=True,
        check=True,
        shell=False,
    )
    staged_files = result.stdout.strip().split("\n")
    migration_files = [
        f for f in staged_files if "migrations/" in f and f.endswith(".py")
    ]
    if not migration_files:
        return []
    diff_result = subprocess.run(  # nosec B603
        shlex.split("git diff --cached") + migration_files,
        capture_output=True,
        text=True,
        check=True,
        shell=False,
    )
    return diff_result.stdout


def extract_new_fields(diff_content):
    """Extract model and field names.
    Extract model and field names from AddField operations in
    staged migrations.
    """
    add_field_pattern = (
        r"migrations\.AddField\([^)]*"
        r"model_name\s*=\s*['\"](\w+)['\"]"
        r"[^)]*name\s*=\s*['\"](\w+)['\"]"
    )
    return re.findall(add_field_pattern, diff_content, re.DOTALL)


def extract_new_models(diff_content):
    """Extract model names from CreateModel operations."""
    return re.findall(
        r"migrations\.CreateModel\(.*?name\s*=\s*['\"](\w+)['\"]",
        diff_content,
        re.DOTALL,
    )


def check_fields_in_config(new_fields, config_path, writer):
    """Check which fields are missing from anonymiser config."""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError as e:
        writer.warning(f"Warning: Could not read config file: {e}")
        return []
    strategy = config.get("strategy", {})
    missing = []
    for model_name, field_name in new_fields:
        if model_name not in strategy or field_name not in strategy[model_name]:
            missing.append(f"{model_name}.{field_name}")
    return missing
