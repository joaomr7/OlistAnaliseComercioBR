from src.config.configuration import ConfigurationManager

from src.components.data_ingestion import DataIngestion
from src.components.data_preprocessing import DataPreprocessing
from src.components.lda.data_ingestion import LDADataIngestion
from src.components.lda.data_transformation import LDADataTranformation
from src.components.lda.model_trainer import LDAModelTrainer

from src.utils.exception import CustomException

try:
    config_manager = ConfigurationManager()

    # main data ingestion
    data_ingestion_config = config_manager.get_data_ingestion_config()
    data_ingestion = DataIngestion(data_ingestion_config)
    data_ingestion.initiate_data_ingestion()

    # lda data ingestion
    lda_data_ingestion_config = config_manager.get_lda_data_ingestion_config()
    lda_data_ingestion = LDADataIngestion(lda_data_ingestion_config)
    lda_data_ingestion = LDADataIngestion(lda_data_ingestion_config)
    lda_data_ingestion.initiate_data_ingestion()

    # lda data tranformation
    lda_data_transformation_config = config_manager.get_lda_data_transformation_config()
    lda_data_transformation = LDADataTranformation(lda_data_transformation_config)
    lda_data_transformation.initiate_data_transformation()

    # lda model trainer
    lda_model_trainer_config = config_manager.get_lda_model_trainer_config()
    lda_model_trainer = LDAModelTrainer(lda_model_trainer_config)
    lda_model_trainer.initiate_model_trainer()

    # main data preprocessing
    data_preprocessing_config = config_manager.get_data_preprocessing_config()
    data_preprocessing = DataPreprocessing(data_preprocessing_config)
    data_preprocessing.initiate_data_preprocessing()

except Exception as e:
    raise CustomException(e)