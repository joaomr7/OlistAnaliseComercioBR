import os
from pathlib import Path
import pandas as pd

from src.utils.exception import CustomException
from src.entity.config_entity import LDADataTransformationConfig
from src.utils.common import create_directories, save_obj
from src.utils import logger

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.pipeline import Pipeline

import re
import spacy
from spacy.tokens import Doc
from spacy.lang.pt.stop_words import STOP_WORDS

class LDADataTranformation:
    def __init__(self, config: LDADataTransformationConfig):
        self.config = config

    def get_data_transformer_object(self):
        try:
            transformer = Pipeline(
                steps=[
                    ('preprocessing', TextPreprocessing(
                        self.config.custom_stop_words,
                        self.config.typos_correction,
                        self.config.words_substitution
                    )),
                    ('vectorizer', TextVectorizer(
                        self.config.max_ngram,
                        self.config.max_df,
                        self.config.min_df,
                        self.config.max_features
                    ))
                ]
            )

            return transformer

        except Exception as e:
            raise CustomException(e)

    def initiate_data_transformation(self):
        logger.info('starting lda data transformation.')

        try:
            train_data = pd.read_csv(self.config.train_data_path)
            test_data = pd.read_csv(self.config.test_data_path)

            logger.info('read train and test data completed.')

            logger.info('obtaining preprocessing object.')
            preprocessing_obj = self.get_data_transformer_object()

            # call fit_transform manually for training data
            train_data_result = preprocessing_obj.named_steps['preprocessing'].train(train_data['reviews'])
            train_data_result = preprocessing_obj.named_steps['vectorizer'].fit_transform(train_data_result)
            train_result_df = pd.DataFrame({'vectors' : train_data_result.toarray().tolist()})

            test_data_result = preprocessing_obj.transform(test_data['reviews'])
            test_result_df = pd.DataFrame({'vectors' : test_data_result.toarray().tolist()})

            # create destiny directorysss
            dest_dir = Path(self.config.dest_dir)
            create_directories([dest_dir])

            # save train and test results
            logger.info(f'saving data tranformation results at: {dest_dir}')
            train_result_df.to_csv(dest_dir / self.config.dest_train_filename)
            test_result_df.to_csv(dest_dir / self.config.dest_test_filename)

            # save transformer object
            save_obj(dest_dir / self.config.transformer_obj_filename, preprocessing_obj)
            
        except Exception as e:
            raise CustomException(e)

class TextPreprocessing(BaseEstimator, TransformerMixin):
    '''
    TextPreprocessing
    -----------------
    Helper class that applies preprocessing to texts before vectorization.

    Attributes:
    -----------
    custom_stop_words : list[str]
        Custom stopwords to be removed from the given texts.

    typos_correction : dict[str, str]
        A dictionary of corrections for common typos.

    words_substitution : dict[str, list[str]]
        A dictionary with words and their possible replacements.
    '''

    def __init__(self,
                 custom_stop_words,
                 typos_correction,
                 words_substitution,
                 nlp=None) -> None:
        self.__nlp = nlp

        self.custom_stop_words = custom_stop_words
        self.typos_correction = typos_correction
        self.words_substitution = words_substitution

        self.__training = False

    def __reduce__(self):
        # do not serialize __nlp
        return (self.__class__, (
            self.custom_stop_words,
            self.typos_correction,
            self.words_substitution,
            None
        ))

    def __initialize_nlp(self):
        '''
        Helper function to load portuguese spacy model.
        '''
        try:
            if self.__nlp is None:
                self.__nlp = spacy.load('pt_core_news_md', disable=['parser', 'ner', 'textcat', 'custom'])
        
        except Exception as e:
            raise CustomException(e)

    def train(self, X):
        '''
        Helper function used just for training LDA model. If you are not training the LDA model, then use fit_transform.
        '''
        self.__training = True
        X_transformed = self.fit_transform(X)
        self.__training = False

        return X_transformed

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        try:
            self.__initialize_nlp()

            # fix typos
            correct_texts = []
            for text in X:
                correct = text.lower()

                for typo, correction in self.typos_correction.items():
                    correct = re.sub(rf'\b{typo}\b', correction, correct)

                correct_texts.append(correct)

            # tranform texts into spacy docs
            docs = [doc for doc in self.__nlp.pipe(correct_texts)]

            # create stopwords
            stopwords = STOP_WORDS | set(self.custom_stop_words)

            docs_clean = []
            for doc in docs:
                words = []

                for token in doc:
                    # ignore token that are not alpha
                    if not token.is_alpha:
                        continue

                    word_lemma = token.lemma_.lower()

                    # ignore stopwords
                    if token.text in stopwords or word_lemma in stopwords:
                        continue

                    # ignore lemma if it's composed of two or more words
                    if len(word_lemma.split()) > 1:
                        continue

                    # make words substitutions
                    for w, subs in self.words_substitution.items():
                        if word_lemma in subs or token.text in subs:
                            word_lemma = w
                            break

                    words.append(word_lemma)

                # remove repeated words one after other
                unique_words = []
                for i, word in enumerate(words):
                    if i < len(words) - 1:
                        if word == words[i + 1]:
                            continue
                    unique_words.append(word)

                if self.__training:
                    # if is training, then ignore docs with no representation or that are present in ignored_single_train_texts
                    if len(unique_words) > 0:
                        spaces = [True] * len(unique_words)
                        spaces[-1] = False

                        final_doc = Doc(self.__nlp.vocab, unique_words, spaces)
                        docs_clean.append(final_doc)

                else:
                    spaces = []
                    if len(unique_words) > 0:
                        spaces = [True] * len(unique_words)
                        spaces[-1] = False

                    docs_clean.append(Doc(self.__nlp.vocab, unique_words, spaces))

            # return each doc as text
            return [doc.text for doc in docs_clean]
    
        except Exception as e:
            raise CustomException(e)
        
class TextVectorizer(BaseEstimator, TransformerMixin):
    '''
    TextVectorizer
    --------------
    A helper class for vectorizing text data.
    
    Attributes
    ----------
    max_ngram : int
        The maximum ngram range to be considered.

    max_df : float [0, 1]
        Ignore words with a higher document frequency (df) than max_df.

    min_df : float [0, 1]
        Ignore words with a lower document frequency (df) than min_df.

    max_features : int
        Max vocabulary size.
    '''

    def __init__(self, max_ngram, max_df, min_df, max_features) -> None:
        self.max_ngram = max_ngram
        self.max_df = max_df
        self.min_df = min_df
        self.max_features = max_features
        self.vectorizer = None

    def fit(self, X, y=None):
        # first uses TFIDF
        tfidf_vectorizer = TfidfVectorizer(
            ngram_range=(1, self.max_ngram),
            strip_accents='unicode',
            max_df=self.max_df,
            min_df=self.min_df,
            max_features=self.max_features,
            binary=True
        )

        tfidf_vectorizer.fit(X)

        # then pass the features from tfidf_vectorizer to the CountVectorizer
        self.vectorizer = CountVectorizer(
            ngram_range=(1, self.max_ngram),
            vocabulary=tfidf_vectorizer.get_feature_names_out().tolist(),
            strip_accents='unicode',
            binary=True
        )

        self.vectorizer.fit(X)

        return self

    def transform(self, X, y=None):
        return self.vectorizer.transform(X)