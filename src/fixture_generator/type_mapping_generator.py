"""Fixture type mapping collection and file generation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, TextIO

from pydantic import BaseModel

from src.fixture_generator.helpers import format_file_with_ruff

if TYPE_CHECKING:
    from src.fixture_generator.fixture_types import FixtureAPIResult

logger = logging.getLogger(__name__)


@dataclass
class FixturePathToTypeMapping:
    """Class for managing fixture type information."""

    key: str  # "tracks/user_history.json"
    fixture_type: type[BaseModel] | None = None

    @property
    def category(self) -> str:
        """Get category name."""
        return self.key.split("/", 1)[0]

    @property
    def filename(self) -> str:
        """Get filename."""
        return self.key.split("/", 1)[1]

    def auto_detect_fixture_type[T: BaseModel](self, response: FixtureAPIResult[T]) -> None:
        """Automatically detect fixture type from API response."""
        # For list case
        if isinstance(response, list):
            if response:  # Only if list is not empty
                first_item = response[0]
                item_type = type(first_item)
                if issubclass(item_type, BaseModel):
                    logger.info(f"Auto-detected list type with items: {item_type.__name__}")
                    self.fixture_type = item_type
            return

        # For single object case
        self.fixture_type = type(response)
        module_name = self.fixture_type.__module__
        logger.info(f"Auto-detected type: {self.fixture_type.__name__} from {module_name}")
        return


class FixtureTypeMappingCollector:
    """Collects fixture type mappings during fixture generation."""

    def __init__(self) -> None:
        """Initialize the collector."""
        self.fixture_mappings: dict[str, FixturePathToTypeMapping] = {}

    def record_type_mapping[T: BaseModel](
        self, response: FixtureAPIResult[T], category: str, name: str
    ) -> FixturePathToTypeMapping:
        """Record type mapping for automatic generation."""
        key = f"{category}/{name}.json"

        mapping = FixturePathToTypeMapping(key=key, fixture_type=None)
        mapping.auto_detect_fixture_type(response)
        self.fixture_mappings[key] = mapping
        return mapping

    def get_all_mappings(self) -> dict[str, type[BaseModel]]:
        """Get all recorded mappings as path -> type dict."""
        return {
            key: mapping.fixture_type
            for key, mapping in self.fixture_mappings.items()
            if mapping.fixture_type is not None
        }


class FixtureTypeMappingFileGenerator:
    """Generates fixture_type_mappings.py file from collected mappings."""

    def __init__(self, mappings: dict[str, type]) -> None:
        """Initialize the generator with mappings.

        Args:
            mappings: Dictionary mapping fixture paths to their types
        """
        self.mappings = mappings
        # Detect the base package by finding the root package of current file
        self._base_package = self._detect_base_package()
        self._target_package_prefix: str | None = None

    def _detect_base_package(self) -> str:
        """Detect the base package name from current file location.

        Returns the top-level package name (e.g., 'src' from 'src.fixture_generator.xxx').
        """
        current_module = self.__class__.__module__
        # Get the first component of the module path
        return current_module.split(".", 1)[0]

    def _detect_target_package_from_path(self, output_path: Path) -> str:
        """Detect target package prefix from output file path.

        Args:
            output_path: Path where the file will be generated

        Returns:
            Package prefix (e.g., 'src.fixture_data' from 'src/fixture_data/file.py')

        Raises:
            ValueError: If target package cannot be detected from output path
        """
        # Find the package path relative to project root
        # Walk up from current file to find project root (where src/ exists)
        current_file = Path(__file__)
        for parent in current_file.parents:
            if (parent / self._base_package).is_dir():
                # Found project root, now calculate relative path
                try:
                    rel_path = output_path.parent.relative_to(parent)
                    # Convert path to module notation
                    return str(rel_path).replace("/", ".")
                except ValueError:
                    # output_path is not relative to this parent
                    continue

        # Could not detect target package
        msg = f"Failed to detect target package from output path: {output_path}"
        raise ValueError(msg)

    def generate_file(self, output_path: Path) -> None:
        """Generate the fixture_type_mappings.py file.

        Args:
            output_path: Path to the generated fixture_type_mappings.py file
        """
        # Detect target package from output path
        self._target_package_prefix = self._detect_target_package_from_path(output_path)

        # Collect imports
        imports = self._collect_imports()

        # Write file
        with output_path.open("w", encoding="utf-8") as f:
            self._write_header(f)
            self._write_imports(f, imports)
            self._write_type_checking_block(f)
            self._write_mappings(f)

        logger.info(f"Generated path->type mapping at {output_path}")
        logger.info("Note: Run 'ruff check --fix' to format the generated files")

        # Format with ruff
        format_file_with_ruff(output_path)

    def _collect_imports(self) -> set[tuple[str, str]]:
        """Collect all required imports from fixture mappings."""
        needed_imports = set()

        for fixture_type in self.mappings.values():
            if fixture_type and isinstance(fixture_type, type):
                module = fixture_type.__module__

                # Simple rule: Include all types that are not from built-in/standard library
                # This automatically handles external libraries and local project modules
                if not module.startswith(("builtins", "__", "typing")):
                    # Convert modules from same package tree to relative imports
                    # since the generated file will be copied to server project
                    if self._target_package_prefix and module.startswith(
                        f"{self._target_package_prefix}."
                    ):
                        # Convert src.fixture_data.shared_types -> .shared_types
                        relative_module = module.replace(f"{self._target_package_prefix}.", ".")
                        needed_imports.add((relative_module, fixture_type.__name__))
                    else:
                        needed_imports.add((module, fixture_type.__name__))

        return needed_imports

    def _write_header(self, f: TextIO) -> None:
        """Write file header."""
        f.write('"""Fixture type mappings for automatic deserialization."""\n\n')
        f.write("from __future__ import annotations\n\n")
        f.write("from typing import TYPE_CHECKING\n\n")

    def _write_imports(self, f: TextIO, imports: set[tuple[str, str]]) -> None:
        """Write the imports section."""
        if imports:
            f.writelines(f"from {module} import {name}\n" for module, name in imports)
            f.write("\n")

    def _write_type_checking_block(self, f: TextIO) -> None:
        """Write TYPE_CHECKING block."""
        f.write("if TYPE_CHECKING:\n")
        f.write("    from pydantic import BaseModel\n")
        f.write("\n")

    def _write_mappings(self, f: TextIO) -> None:
        """Generate simple path to type mapping variable."""
        f.write("# Fixture type mappings: path -> type\n")
        f.write("FIXTURE_TYPE_MAPPINGS: dict[str, type[BaseModel]] = {\n")

        entries = []
        for key, fixture_type in self.mappings.items():
            type_name = fixture_type.__name__
            entries.append(f'    "{key}": {type_name},\n')

        f.writelines(entries)
        f.write("}\n")
