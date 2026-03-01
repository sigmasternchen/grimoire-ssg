from dataclasses import dataclass, field
from typing import Any


@dataclass
class Context:
    output_dir: str
    config_file: str | None
    filenames: str
    enabled_modules: list[str] = field(default_factory=lambda: [])
    tags: dict[str, Any] = field(default_factory=lambda: {})
