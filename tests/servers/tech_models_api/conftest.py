"""Pytest configuration for tech_models_api tests."""

import sys
from pathlib import Path

# Add the example server to the path
test_dir = Path(__file__).parent
repo_root = test_dir.parent.parent
tech_models_path = repo_root / "examples" / "servers" / "tech-models-api"

# Insert at the beginning of sys.path
if str(tech_models_path) not in sys.path:
    sys.path.insert(0, str(tech_models_path))
