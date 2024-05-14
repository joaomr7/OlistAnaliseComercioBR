from dataclasses import dataclass
from pathlib import Path

from typing import List, Dict

@dataclass(frozen=True)
class DataIngestionConfig:
    source_dir: Path
    dest_dir: Path
    dest_filename: str

@dataclass(frozen=True)
class LDADataIngestionConfig:
    dest_dir: Path
    dest_filename: str
    dest_train_filename: str
    dest_test_filename: str
    source_data_path: Path

@dataclass(frozen=True)
class LDADataTransformationConfig:
    dest_dir: Path
    transformer_obj_filename: str
    dest_train_filename: str
    dest_test_filename: str
    train_data_path: Path
    test_data_path: Path

    max_ngram: int
    max_df: float
    min_df: float
    max_features: int
    custom_stop_words: List[str]
    typos_correction: Dict[str, str]
    words_substitution: Dict[str, List[str]]

@dataclass(frozen=True)
class LDAModelTrainerConfig:
    dest_dir: Path
    model_filename: str
    train_data_path: Path
    test_data_path: Path

    n_components: int
    doc_prior: float
    word_prior: float
    max_iter: int