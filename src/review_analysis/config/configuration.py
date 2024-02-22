from src.review_analysis.constants import *
from src.review_analysis.utils.common import read_yaml, create_directories

from src.review_analysis.entity.config_entity import DataIngestionConfig

class ConfigurationManager:
    def __init__(self, config_filepath=CONFIG_FILE_PATH):
        self.config = read_yaml(config_filepath)

        # create artifacts root directory
        create_directories([self.config.artifacts_root])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        data_ingestion_config = DataIngestionConfig(
            source_dir=config.source_dir,
            dest_dir=config.dest_dir,
            dest_filename=config.dest_filename
        )

        return data_ingestion_config