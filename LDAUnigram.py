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

class LDAUnigram:
    def __init__(self,body_text):
        self.body_text = body_text
    def performLDA(self):
        nltk.download('stopwords')
        stop_words = stopwords.words('english')

        # paths = ['CORD-19-research-challenge/comm_use_subset/comm_use_subset/pdf_json/',
        #         'CORD-19-research-challenge/biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/',
        #         'CORD-19-research-challenge/custom_license/custom_license/pdf_json/',
        #         'CORD-19-research-challenge/noncomm_use_subset/noncomm_use_subset/pdf_json/']
        # paths = ['CORD-19-research-challenge/comm_use_subset/comm_use_subset/pdf_json/']
        #
        # documents = []
        # # Iterating through documents and retrieving the relevant fields
        # for path in paths:
        #     print('PATH' + path)
        #     for file in os.listdir(path):
        #         # Open the json film corpus
        #         fullFilePath = path + file
        #         currentDoc = json.load(open(fullFilePath, 'rb'))
        #
        #         try:
        #             abstract = currentDoc['abstract'][0]['text']
        #         except:
        #             abstract = ''
        #
        #         documents.append([currentDoc['paper_id'],currentDoc['metadata']['title'],
        #                           currentDoc['body_text'][0]['text'], abstract])
        #
        # df = pd.DataFrame(documents,columns=['paper_id','title','body_text','abstract'])
        #
        # print('Before Tokenization')

        # Convert to list and tokenize
        # data = list(df.body_text.values + df.title.values + df.abstract.values)
        data = ["Hey this is for a test and for a topic model","Yup its a topic model and this is a test you know it"]

        data_words = []
        for doc in data:
            data_words.append(nltk.word_tokenize(doc))

        #Removing stop words
        data_words_nostops = [[word for word in simple_preprocess(str(doc)) if word not in stop_words and word.isalnum()] for doc in data_words]

        print('After stop words')

        # Lemmatization
        lemmaifier = WordNetLemmatizer()

        data_lemmatized = [[lemmaifier.lemmatize(word) for word in doc] for doc in data_words_nostops]

        print('After lemmatization')

        # Create Dictionary
        id2word = corpora.Dictionary(data_lemmatized)

        # Create Corpus
        texts = data_lemmatized

        # Term Document Frequency
        corpus = [id2word.doc2bow(text) for text in texts]

        print('Right before model')

        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                    id2word=id2word,
                                                    num_topics=14,
                                                    random_state=100,
                                                    update_every=1,
                                                    chunksize=100,
                                                    passes=10,
                                                    alpha='auto',
                                                    per_word_topics=True)


        # topic_file = open('/COVID_19-Kaggle_Task_2/topics.txt','w')
        # topic_file.write(lda_model.show_topics())
        # topic_file.close()

        def format_topics_sentences(ldamodel=lda_model, corpus=corpus, texts=data):
            # Init output
            sent_topics_df = pd.DataFrame()

            # # Get main topic in each document
            for i, row in enumerate(ldamodel[corpus]):
                row = sorted(row, key=lambda x: (x[1]), reverse=True)
            #     # Get the Dominant topic, Perc Contribution and Keywords for each document
            # for i, row in enumerate(ldamodel[corpus]):
                for j, (topic_num, prop_topic) in enumerate(row):
                    if j == 0:  # => dominant topic
                        wp = ldamodel.show_topic(topic_num)
                        topic_keywords = ", ".join([word for word, prop in wp])
                        if(type(prop_topic)==list):
                            prop_topic = prop_topic[0]
                        sent_topics_df = sent_topics_df.append(
                            pd.Series([int(topic_num), round(prop_topic, 4), topic_keywords]), ignore_index=True)
                    else:
                        break
            sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']

            # Add original text to the end of the output
            contents = pd.Series(texts)
            sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
            return (sent_topics_df)

        df_topic_sents_keywords = format_topics_sentences(ldamodel=lda_model, corpus=corpus, texts=texts)

        # Format
        df_dominant_topic = df_topic_sents_keywords.reset_index()
        df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text']

        # Show
        df_dominant_topic.head(10)