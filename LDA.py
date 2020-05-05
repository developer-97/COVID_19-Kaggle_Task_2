import nltk
from nltk.corpus import stopwords
import string
from nltk.stem import WordNetLemmatizer
import re
import numpy as np
import pandas as pd
from pprint import pprint

# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

# spacy for lemmatization
import spacy

# Plotting tools
# import pyLDAvis
# import pyLDAvis.gensim  # don't skip this
# import matplotlib.pyplot as plt

# Enable logging for gensim - optional
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

class LDA:
    def __init__(self, body_text):
        self.body_text = body_text
        # self.abstract = abstract

    def performLDA(self):
        # nltk.download('stopwords')
        # stop_words = stopwords.words('english')
        # stop_words.extend(['from', 'subject', 're', 'edu', 'use'])

        #Tokenizing and making tokens into bigrams
        tokens = nltk.word_tokenize(str(self.body_text))
        bigram = gensim.models.Phrases(tokens, min_count=5, threshold=100)
        bigram_mod = gensim.models.phrases.Phraser(bigram)

        #Lemmatization of words
        lemmatized_words = []
        lemmaifier = WordNetLemmatizer()

        for token in tokens:
            if not (len(token) == 1 and token in string.punctuation):
                lemmatized_words.append(lemmaifier.lemmatize(token).lower())

        dictionary = corpora.Dictionary(lemmatized_words)
        texts = lemmatized_words
        corpus = [dictionary.doc2bow(text) for text in texts]

        #Building LDA Model
        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                    id2word=dictionary,
                                                    num_topics=20,
                                                    random_state=100,
                                                    update_every=1,
                                                    chunksize=100,
                                                    passes=10,
                                                    alpha='auto',
                                                    per_word_topics=True)
        print(lda_model.print_topics())
