#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import requests
from jsonschema import validate, ValidationError

SCHEMA_URL = "https://raw.githubusercontent.com/imranq2/language_model_gateway/main/language_model_gateway/configs/config_schema.json"


def download_schema(cache_dir: Path | None = None) -> dict:
    """Download the Language Model Gateway schema with optional caching."""
    if cache_dir:
        cache_file = cache_dir / 'lmg_schema.json'
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Check if cached schema exists and is recent (less than 1 day old)
        if cache_file.exists():
            cache_stat = cache_file.stat()
            cache_age = datetime.now() - datetime.fromtimestamp(cache_stat.st_mtime)
            if cache_age < timedelta(days=1):
                with open(cache_file, 'r') as f:
                    return json.load(f)

    # Download fresh schema
    response = requests.get(SCHEMA_URL)
    response.raise_for_status()
    schema = response.json()

    # Cache the schema if cache_dir is provided
    if cache_dir:
        with open(cache_file, 'w') as f:
            json.dump(schema, f)

    return schema


def validate_json_file(file_path: str | Path, schema: dict) -> bool:
    """Validate a single JSON file against the LMG schema."""
    try:
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        validate(instance=json_data, schema=schema)
        print(f"✅ {file_path} is valid")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ {file_path} is not valid JSON: {str(e)}", file=sys.stderr)
        return False
    except ValidationError as e:
        print(f"❌ {file_path} failed schema validation: {str(e)}", file=sys.stderr)
        return False


def main(argv: list[str] | None = None) -> int:
    """Validate Language Model Gateway configuration files."""
    if argv is None:
        argv = sys.argv[1:]

    try:
        # Use cache directory in user's home
        cache_dir = Path.home() / '.cache' / 'lmg-config-validator'
        schema = download_schema(cache_dir)
    except Exception as e:
        print(f"Failed to download schema: {str(e)}", file=sys.stderr)
        return 1

    success = True
    for file_path in argv:
        if Path(file_path).suffix.lower() == '.json':
            if not validate_json_file(file_path, schema):
                success = False

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
