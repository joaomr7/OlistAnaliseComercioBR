import os
from pathlib import Path
import pandas as pd

from src.utils.exception import CustomException
from src.entity.config_entity import DataIngestionConfig
from src.utils.common import create_directories
from src.utils import logger

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def initiate_data_ingestion(self):
        logger.info('starting data ingestion.')

        try:
            # load datasets
            datasets = {}
            datasets_dir = Path(self.config.source_dir)

            for dataset_filename in os.listdir(datasets_dir):
                # remvove 'olist_' and '_dataset' from filenames
                datasets[Path(
                    dataset_filename.\
                    replace('olist_', '').\
                    replace('_dataset', '')).stem] = pd.read_csv(datasets_dir / dataset_filename)
                
            # join datasets
            final_dataset = datasets['orders'].copy()

            final_dataset = final_dataset.merge(datasets['order_reviews'], how='left', on='order_id')
            final_dataset = final_dataset.merge(datasets['order_payments'], how='left', on='order_id')
            final_dataset = final_dataset.merge(datasets['order_items'], how='left', on='order_id')
            final_dataset = final_dataset.merge(datasets['products'], how='left', on='product_id')
            final_dataset = final_dataset.merge(datasets['sellers'], how='left', on='seller_id')
            final_dataset = final_dataset.merge(datasets['customers'], how='left', on='customer_id')

            # prepare geolocations

            # remover duplicated geolocations
            unique_geolocations = datasets['geolocation'].drop_duplicates().copy()

            # remove irrelevant information
            unique_geolocations.drop(['geolocation_city', 'geolocation_state'], axis=1, inplace=True)

            # calculate mean location
            mean_locations = unique_geolocations.groupby('geolocation_zip_code_prefix').agg({  
                'geolocation_lat' : 'mean',
                'geolocation_lng': 'mean'
                }).reset_index()
            
            # rename geolocation_lat and geolocation_lng to mean_lat and mean_lon
            # also, rename geolocation_zip_code_prefix to zip_code_prefix
            mean_locations.columns = ['zip_code_prefix', 'mean_lat', 'mean_lon']

            # join geolocation to final_dataset
            final_dataset = final_dataset.merge(
                mean_locations,
                how='left',
                left_on='customer_zip_code_prefix',
                right_on='zip_code_prefix')

            final_dataset = final_dataset.merge(
                mean_locations,
                how='left',
                left_on='seller_zip_code_prefix',
                right_on='zip_code_prefix',
                suffixes=['_costumer', '_seller'])
            
            # drop irrelevant columns
            final_dataset.drop(
                ['customer_id', 
                'customer_zip_code_prefix', 
                'zip_code_prefix_costumer',
                'seller_zip_code_prefix',
                'zip_code_prefix_seller'], axis=1, inplace=True)
            
            # save final_dataset
            dest_filename = Path(self.config.dest_dir + '/' + self.config.dest_filename)
            logger.info(f'saving data ingestion result at: {dest_filename}')

            create_directories([self.config.dest_dir])
            final_dataset.to_csv(dest_filename, index=False, header=True)

        except Exception as e:
            raise CustomException(e)