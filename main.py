from src.review_analysis.config.configuration import ConfigurationManager
from src.review_analysis.components.data_ingestion import DataIngestion
from src.review_analysis.utils.exception import CustomException

try:
    config_manager = ConfigurationManager()

    data_ingestion_config = config_manager.get_data_ingestion_config()
    data_ingestion = DataIngestion(data_ingestion_config)

    data_ingestion.initiate_data_ingestion()

except Exception as e:
    raise CustomException(e)