from src.constants import LDA_MODEL_PATH, LDA_PREPROCESSOR_PATH
from src.utils.common import load_object
from src.utils.exception import CustomException

import numpy as np

class PredictPipeline:

    def __init__(self):
        self.__load_objects()

    def __load_objects(self):
        self.__model = load_object(LDA_MODEL_PATH)
        self.__preprocessor = load_object(LDA_PREPROCESSOR_PATH)
        self.__topic_threshold = 0.15

    def predict_review(self, reviews):
        try:
            prepared_reviews = self.__preprocessor.transform(reviews)
            reviews_topics = self.__model.transform(prepared_reviews)

            out_topics = []
            for i, topic in enumerate(reviews_topics):
                if prepared_reviews[i].sum() == 0 or np.abs(topic[0] - topic[1]) <= self.__topic_threshold:
                    out_topics.append('Inconclusive')
                elif topic[0] > topic[1]:
                    out_topics.append('Product')
                else:
                    out_topics.append('Delivery')

            return out_topics

        except Exception as e:
            raise CustomException(e)