from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DataIngestionConfig:
    source_dir: Path
    dest_dir: Path
    dest_filename: str