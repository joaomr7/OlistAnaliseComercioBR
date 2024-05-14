import os
from pathlib import Path
import pandas as pd
import numpy as np
import ast

from src.utils.exception import CustomException
from src.entity.config_entity import LDAModelTrainerConfig
from src.utils.common import create_directories, save_obj
from src.utils import logger

from sklearn.decomposition import LatentDirichletAllocation

class LDAModelTrainer:
    def __init__(self, config: LDAModelTrainerConfig) -> None:
        self.config = config

    def initiate_model_trainer(self):
        logger.info('starting lda model trainer.')

        try:
            # load train and test data
            train_data_df = pd.read_csv(self.config.train_data_path)
            test_data_df = pd.read_csv(self.config.test_data_path)

            logger.info('read train and test data completed.')

            # transform data vectors into numpy array
            train_data = [np.array(ast.literal_eval(train_vec)) for train_vec in train_data_df['vectors']]
            test_data = [np.array(ast.literal_eval(test_vec)) for test_vec in test_data_df['vectors']]

            logger.info('creating and training model...')
            lda_model = LatentDirichletAllocation(
                n_components=self.config.n_components,
                doc_topic_prior=self.config.doc_prior,
                topic_word_prior=self.config.word_prior,
                max_iter=self.config.max_iter,
                random_state=42
            )

            lda_model.fit(train_data)

            # calculate perplecity for train and test data
            train_perplexity = lda_model.perplexity(train_data)
            test_perplexity = lda_model.perplexity(test_data)

            logger.info(f'lda model perplexity on training data: {train_perplexity}')
            logger.info(f'lda model perplexity on testing data: {test_perplexity}')

            # create destiny directorysss
            dest_dir = Path(self.config.dest_dir)
            create_directories([dest_dir])

            # save model
            logger.info(f'saving model at: {dest_dir / self.config.model_filename}')
            save_obj(dest_dir / self.config.model_filename, lda_model)

        except Exception as e:
            raise CustomException(e)