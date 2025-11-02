"""Helper functions for nicovideo fixture generation."""

from __future__ import annotations

import logging
import subprocess
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel

from src.fixture_generator.fixture_types import FixtureAPIResult, JsonContainer, JsonDict, JsonList

if TYPE_CHECKING:
    from mashumaro import DataClassDictMixin
    from pydantic import JsonValue

logger = logging.getLogger(__name__)

T = TypeVar("T")


def find_project_root(start_path: Path | None = None) -> Path | None:
    """Find project root by looking for pyproject.toml.

    Args:
        start_path: Starting path to search from. If None, uses the caller's file location.

    Returns:
        Path to project root, or None if not found.
    """
    if start_path is None:
        start_path = Path(__file__).resolve()

    current = start_path if start_path.is_dir() else start_path.parent

    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent

    return None


def format_file_with_ruff(file_path: Path) -> bool:
    """Format a file with ruff (check and format).

    Args:
        file_path: Path to the file to format

    Returns:
        True if formatting succeeded, False otherwise
    """
    project_root = find_project_root()

    if not project_root:
        logger.warning("Could not find project root (pyproject.toml), skipping ruff formatting")
        return False

    ruff_path = project_root / ".venv" / "bin" / "ruff"

    if not ruff_path.exists():
        logger.warning(f"ruff not found at {ruff_path}, skipping formatting")
        return False

    try:
        # Run ruff check --fix for linting fixes
        subprocess.run(  # noqa: S603
            [str(ruff_path), "check", "--fix", str(file_path)],
            check=True,
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        logger.info(f"Formatted {file_path} with ruff")
        return True

    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to format {file_path} with ruff: {e.stderr}")
        return False
    except FileNotFoundError as e:
        logger.warning(f"ruff command not found: {e}, skipping formatting")
        return False


def sort_dict_keys_and_lists(obj: JsonValue) -> JsonValue:
    """Sort dictionary keys and list elements for consistent snapshot comparison.

    This function ensures deterministic ordering by:
    - Sorting dictionary keys alphabetically
    - Sorting list elements by type and string representation

    Particularly useful for handling serialized sets that would otherwise have
    random ordering between test runs.
    """
    if isinstance(obj, dict):
        # Sort dictionary keys and recursively process values
        return {key: sort_dict_keys_and_lists(obj[key]) for key in sorted(obj.keys())}
    if isinstance(obj, list):
        # Recursively process list items first
        sorted_items = [sort_dict_keys_and_lists(item) for item in obj]
        try:
            # Sort items for deterministic ordering (handles serialized sets)
            return sorted(sorted_items, key=lambda x: (type(x).__name__, str(x)))
        except (TypeError, ValueError):
            # If sorting fails, return in original order
            return sorted_items
    else:
        # Return primitive values as-is
        return obj


def to_dict_for_snapshot(media_item: DataClassDictMixin) -> JsonDict:
    """Convert DataClassDictMixin to dict with sorted keys and lists for snapshot comparison."""
    # Get the standard to_dict representation
    item_dict = media_item.to_dict()

    # Recursively sort all nested structures, especially sets
    sorted_result = sort_dict_keys_and_lists(item_dict)

    # Ensure we return the expected dict type
    if isinstance(sorted_result, dict):
        return sorted_result
    # This should not happen given the input, but satisfies mypy
    return item_dict


def to_dict_for_fixture[T: BaseModel](response: FixtureAPIResult[T]) -> JsonContainer:
    """Convert response to JSON serializable format."""
    # Check for Pydantic models first
    if isinstance(response, BaseModel):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return response.model_dump(by_alias=True)
    data: JsonList = []
    for item in response:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data.append(item.model_dump(by_alias=True))
    return data
