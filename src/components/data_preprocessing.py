import pandas as pd
import numpy as np

from pathlib import Path

from src.utils.exception import CustomException
from src.entity.config_entity import DataPreprocessingConfig
from src.pipeline.predict_pipeline import PredictPipeline
from src.utils.common import create_directories
from src.utils import logger

class DataPreprocessing:
    def __init__(self, config: DataPreprocessingConfig):
        self.config = config

    def initiate_data_preprocessing(self):
        logger.info('starting data preprocessing.')

        try:
            # load dataset
            df = pd.read_csv(self.config.source_data_path)

            # drop unused variables
            df.drop([
                'payment_sequential', 'payment_type', 'payment_installments', 'payment_value',
                'product_category_name', 'product_name_lenght', 'product_description_lenght',
                'product_photos_qty', 'product_weight_g', 'product_length_cm', 'product_height_cm',
                'product_width_cm', 'mean_lat_costumer', 'mean_lon_costumer', 'mean_lat_seller',
                'mean_lon_seller', 'order_item_id', 'order_approved_at', 'order_delivered_carrier_date', 
                'review_creation_date', 'review_answer_timestamp',
                'seller_id', 'shipping_limit_date', 'price', 'freight_value', 'seller_city',
                'seller_state', 'customer_unique_id', 'customer_city', 'customer_state'
            ], axis=1, inplace=True)

            # parse date variables
            for column in df.columns:
                if column.endswith(('_date', '_timestamp', '_at')):
                    df[column] = pd.to_datetime(df[column])

            # remove duplicates
            df.drop_duplicates(inplace=True)

            # join review title and message
            df['reviews'] = df.review_comment_title + '. ' + df.review_comment_message

            # predict review complaint type
            df['complaint'] = np.nan
            df.complaint = df.complaint.astype(object)

            predict_pipeline = PredictPipeline()
            low_score_reviews = df[df.review_score <= 2].reviews.dropna()
            predicted_complaint = predict_pipeline.predict_review(low_score_reviews)
            df.loc[low_score_reviews.index, 'complaint'] = predicted_complaint

            # drop reviews
            df.drop(['reviews', 'review_comment_title', 'review_comment_message'], axis=1, inplace=True)

            # save prepared data
            dest_filename = Path(self.config.dest_dir + '/' + self.config.dest_filename)
            logger.info(f'saving data preprocessing result at: {dest_filename}')

            create_directories([self.config.dest_dir])
            df.to_csv(dest_filename, index=False, header=True)

        except Exception as e:
            raise CustomException(e)