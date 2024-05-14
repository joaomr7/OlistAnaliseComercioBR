import os
from pathlib import Path
import pandas as pd

from src.utils.exception import CustomException
from src.entity.config_entity import LDADataIngestionConfig
from src.utils.common import create_directories
from src.utils import logger

from sklearn.model_selection import train_test_split

class LDADataIngestion:
    def __init__(self, config: LDADataIngestionConfig):
        self.config = config

    def initiate_data_ingestion(self):
        logger.info('starting data ingestion for LDA model.')

        try:
            # load source data
            source_df = pd.read_csv(self.config.source_data_path)

            # keep just instances where review_score is less or equal to 3
            source_df = source_df[source_df.review_score <= 3]

            # join review title and message
            reviews = source_df.review_comment_title + '. ' + source_df.review_comment_message

            # remove null or duplicated reviews
            reviews.dropna(inplace=True)
            reviews.drop_duplicates(inplace=True)
            reviews = reviews.to_frame(name='reviews')

            # split train and test data
            reviews_train, reviews_test = train_test_split(reviews, test_size=0.2, random_state=42)

            # save files
            dest_filename = Path(self.config.dest_dir + '/' + self.config.dest_filename)
            dest_train_filename = Path(self.config.dest_dir + '/' + self.config.dest_train_filename)
            dest_test_filename = Path(self.config.dest_dir + '/' + self.config.dest_test_filename)
            
            logger.info(f'saving data ingestion result at: {dest_filename}, {dest_train_filename}, {dest_test_filename}')

            create_directories([self.config.dest_dir])
            reviews.to_csv(dest_filename, index=False, header=True)
            reviews_train.to_csv(dest_train_filename, index=False, header=True)
            reviews_test.to_csv(dest_test_filename, index=False, header=True)

        except Exception as e:
            raise CustomException(e)