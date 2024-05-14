from src.constants import *
from src.utils.common import read_yaml, create_directories

from src.entity.config_entity import DataIngestionConfig
from src.entity.config_entity import LDADataIngestionConfig
from src.entity.config_entity import LDADataTransformationConfig
from src.entity.config_entity import LDAModelTrainerConfig

class ConfigurationManager:
    def __init__(self, config_filepath=CONFIG_FILE_PATH, params_filepath=PARAMETERS_FILE_PATH):
        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)

        # create artifacts and lda root directory
        create_directories([self.config.artifacts_root, self.config.lda.root_dir])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        data_ingestion_config = DataIngestionConfig(
            source_dir=config.source_dir,
            dest_dir=config.dest_dir,
            dest_filename=config.dest_filename
        )

        return data_ingestion_config
    
    def get_lda_data_ingestion_config(self) -> LDADataIngestionConfig:
        config = self.config.lda.data_ingestion

        data_ingestion_config = LDADataIngestionConfig(
            dest_dir=config.dest_dir,
            dest_filename=config.dest_filename,
            dest_train_filename=config.dest_train_filename,
            dest_test_filename=config.dest_test_filename,
            source_data_path=config.source_data_path
        )

        return data_ingestion_config

    def get_lda_data_transformation_config(self) -> LDADataTransformationConfig:
        config = self.config.lda.data_transformation
        params = self.params.lda_data_tranformation_params

        data_transformation_config = LDADataTransformationConfig(
            dest_dir=config.dest_dir,
            transformer_obj_filename=config.transformer_obj_filename,
            dest_train_filename=config.dest_train_filename,
            dest_test_filename=config.dest_test_filename,
            train_data_path=config.train_data_path,
            test_data_path=config.test_data_path,
            max_ngram=params.max_ngram,
            max_df=params.max_df,
            min_df=params.min_df,
            max_features=params.max_features,
            custom_stop_words=params.custom_stop_words,
            typos_correction=params.typos_correction,
            words_substitution=params.words_substitution
        )

        return data_transformation_config
    
    def get_lda_model_trainer_config(self) -> LDAModelTrainerConfig:
        config = self.config.lda.model_trainer
        params = self.params.lda_model_params

        model_trainer_config = LDAModelTrainerConfig(
            dest_dir=config.dest_dir,
            model_filename=config.model_filename,
            train_data_path=config.train_data_path,
            test_data_path=config.test_data_path,
            n_components=params.n_components,
            doc_prior=params.doc_prior,
            word_prior=params.word_prior,
            max_iter=params.max_iter
        )

        return model_trainer_config