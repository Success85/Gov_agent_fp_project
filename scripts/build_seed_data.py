"""Build data/seed_data.json from the per-service files in data/services/.

Lane 4 owns the per-service JSON files under data/services/. Those files are the
single source of truth for verified government-service data. The database seeder
(backend/app/db/seed.py) loads data/seed_data.json, so this script combines every
per-service file into that one file.

Run it after editing or adding any service file:

    python scripts/build_seed_data.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# The exact keys seed.py reads. If a file is missing one, we want to fail loudly
# here rather than silently seed incomplete data into the demo database.
REQUIRED_SERVICE_KEYS = {"name", "description", "fee", "requirements", "steps"}
REQUIRED_REQUIREMENT_KEYS = {"name", "description", "mandatory", "needs_upload", "order_index"}
REQUIRED_STEP_KEYS = {"order_index", "description"}


def project_root() -> Path:
    # This file lives in <root>/scripts/, so the project root is one level up.
    return Path(__file__).resolve().parents[1]


def validate_service(data: dict, filename: str) -> None:
    """Raise a clear error if a service file is missing any required key."""
    missing = REQUIRED_SERVICE_KEYS - data.keys()
    if missing:
        raise ValueError(f"{filename}: service is missing keys: {sorted(missing)}")
    for requirement in data["requirements"]:
        missing_req = REQUIRED_REQUIREMENT_KEYS - requirement.keys()
        if missing_req:
            raise ValueError(f"{filename}: a requirement is missing keys: {sorted(missing_req)}")
    for step in data["steps"]:
        missing_step = REQUIRED_STEP_KEYS - step.keys()
        if missing_step:
            raise ValueError(f"{filename}: a step is missing keys: {sorted(missing_step)}")


def build() -> None:
    root = project_root()
    services_dir = root / "data" / "services"
    output_file = root / "data" / "seed_data.json"

    # sorted() gives a deterministic order, so seed_data.json doesn't reshuffle
    # (and create noisy git diffs) just because the filesystem listed files differently.
    service_files = sorted(services_dir.glob("*.json"))
    if not service_files:
        print(f"No service files found in {services_dir}", file=sys.stderr)
        sys.exit(1)

    services: list[dict] = []
    for path in service_files:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        validate_service(data, path.name)
        services.append(data)
        print(
            f"  loaded {path.name}: {data['name']} "
            f"({len(data['requirements'])} requirements, {len(data['steps'])} steps)"
        )

    with output_file.open("w", encoding="utf-8") as handle:
        # ensure_ascii=False keeps any non-ASCII characters (e.g. Kinyarwanda) readable.
        json.dump(services, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"\nWrote {len(services)} services to {output_file.relative_to(root)}")


if __name__ == "__main__":
    build()