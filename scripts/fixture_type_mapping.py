"""Fixture type mapping collection and file generation."""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, TextIO

from pydantic import BaseModel

if TYPE_CHECKING:
    from scripts.types import FixtureAPIResult

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

    def generate_file(self, output_path: Path) -> None:
        """Generate the fixture_type_mappings.py file.

        Args:
            output_path: Path to the generated fixture_type_mappings.py file
        """
        # Collect imports
        imports = self._collect_imports()

        # Write file
        with output_path.open("w", encoding="utf-8") as f:
            self._write_header(f)
            self._write_imports(f, imports)
            self._write_type_checking_block(f)
            self._write_mappings(f)

        # Generate __init__.py file
        self._generate_init_file(output_path.parent)

        logger.info(f"Generated path->type mapping at {output_path}")
        logger.info(f"Generated __init__ at {output_path.parent / '__init__.py'}")
        logger.info("Note: Run 'ruff check --fix' to format the generated files")

        # Format with ruff
        self._format_with_ruff(output_path)

    def _collect_imports(self) -> set[tuple[str, str]]:
        """Collect all required imports from fixture mappings."""
        needed_imports = set()

        for fixture_type in self.mappings.values():
            # Collect import information for fixture_type
            if (
                fixture_type
                and isinstance(fixture_type, type)
                and (
                    fixture_type.__module__.startswith("niconico.")
                    or fixture_type.__module__.startswith("fixture_data.")
                )
            ):
                needed_imports.add((fixture_type.__module__, fixture_type.__name__))

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

    def _generate_init_file(self, generated_dir: Path) -> None:
        """Generate __init__.py file for the generated fixtures package."""
        init_path = generated_dir / "__init__.py"

        with init_path.open("w", encoding="utf-8") as f:
            f.write('"""Generated fixtures for testing."""\n\n')
            f.write("from .fixture_types import FIXTURE_TYPE_MAPPINGS\n\n")
            f.write("__all__ = [\n")
            f.write('    "FIXTURE_TYPE_MAPPINGS",\n')
            f.write("]\n")

    def _format_with_ruff(self, file_path: Path) -> None:
        """Format the generated file with ruff."""
        try:
            # Use ruff from this repository's venv
            fixtures_root = Path(__file__).parent.parent  # music-assistant-nicovideo-fixtures root
            ruff_path = fixtures_root / ".venv" / "bin" / "ruff"

            subprocess.run(  # noqa: S603
                [str(ruff_path), "check", "--fix", str(file_path)],
                check=True,
                capture_output=True,
                text=True,
                cwd=fixtures_root,
            )
            logger.info(f"Formatted {file_path} with ruff")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to format {file_path} with ruff: {e.stderr}")
        except FileNotFoundError as e:
            logger.warning(f"ruff command not found: {e}, skipping formatting")
