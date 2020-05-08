import nltk
from nltk.corpus import stopwords
import string
from nltk.stem import WordNetLemmatizer
import re
import numpy as np
import os
import json
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
    def __init__(self,body_text):
        self.body_text = body_text
    def performLDA(self):
        nltk.download('stopwords')
        stop_words = stopwords.words('english')

        path = 'CORD-19-research-challenge/comm_use_subset/comm_use_subset/pdf_json/'
        documents = []
        # Iterating through documents and retrieving the relevant fields
        for file in os.listdir(path):
            # Open the json film corpus
            fullFilePath = path + file
            currentDoc = json.load(open(fullFilePath, 'rb'))

            try:
                abstract = currentDoc['abstract'][0]['text']
            except:
                abstract = ''

            documents.append([currentDoc['paper_id'],currentDoc['metadata']['title'],
                              currentDoc['body_text'][0]['text'], abstract])

        df = pd.DataFrame(documents,columns=['paper_id','title','body_text','abstract'])

        # Convert to list and tokenize
        data = list(df.body_text.values)
        data_words = []
        for doc in data:
            data_words.append(nltk.word_tokenize(doc))

        # Build the bigram model
        bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100)  # higher threshold fewer phrases.

        # Faster way to get a sentence clubbed as a bigram
        bigram_mod = gensim.models.phrases.Phraser(bigram)

        #Removing stop words
        data_words_nostops = [[word for word in doc if word not in stop_words] for doc in data_words]

        # Form Bigrams
        data_words_bigrams = [bigram_mod[doc] for doc in data_words_nostops]

        # Lemmatization
        lemmaifier = WordNetLemmatizer()

        data_lemmatized = [[lemmaifier.lemmatize(bigram) for bigram in doc] for doc in data_words_bigrams]

        # Create Dictionary
        id2word = corpora.Dictionary(data_lemmatized)

        # Create Corpus
        texts = data_lemmatized

        # Term Document Frequency
        corpus = [id2word.doc2bow(text) for text in texts]

        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                    id2word=id2word,
                                                    num_topics=5,
                                                    random_state=100,
                                                    update_every=1,
                                                    chunksize=100,
                                                    passes=10,
                                                    alpha='auto',
                                                    per_word_topics=True)
        pprint(lda_model.print_topics())