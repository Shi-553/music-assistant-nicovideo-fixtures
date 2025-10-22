"""Helper functions for nicovideo fixture generation."""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel

from src.fixture_generator.types import FixtureAPIResult, JsonContainer, JsonDict, JsonList

if TYPE_CHECKING:
    from mashumaro import DataClassDictMixin
    from pydantic import JsonValue

T = TypeVar("T")


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
