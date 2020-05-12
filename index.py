import json
import re
import sys
import time
import os
from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch_dsl import Index, Document, Text, Integer
from elasticsearch_dsl.analysis import tokenizer, analyzer
from elasticsearch_dsl.connections import connections

# Connect to local host server
connections.create_connection(hosts=['127.0.0.1'])

# Create elasticsearch object
es = Elasticsearch()

# Defining Analyzers

my_analyzer = analyzer('custom',
                       tokenizer='standard',
                       filter=['lowercase', 'stop', 'porter_stem']
                       )



# Define document mapping (schema) by defining a class as a subclass of Document.
# This defines fields and their properties (type and analysis applied).
# You can use existing es analyzers or use ones you define yourself as above.
class Document_COVID_19(Document):
    title = Text(analyzer=my_analyzer)
    paper_id = Text(analyzer='simple')
    abstract = Text(analyzer=my_analyzer)
    body_text = Text(analyzer=my_analyzer)

    # override the Document save method to include subclass field definitions
    def save(self, *args, **kwargs):
        return super(Document_COVID_19, self).save(*args, **kwargs)


# Populate the index
def buildIndex():
    """
    buildIndex creates a new film index, deleting any existing index of
    the same name.
    It loads a json file containing the movie corpus and does bulk loading
    using a generator function.
    """
    film_index = Index('covid_19_index')
    if film_index.exists():
        film_index.delete()  # Overwrite any previous version
    film_index.document(Document_COVID_19)
    film_index.create()

    documents = {}
    # paths = ['CORD-19-research-challenge/biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/',
    #          'CORD-19-research-challenge/comm_use_subset/comm_use_subset/pdf_json/',
    #          'CORD-19-research-challenge/custom_license/custom_license/pdf_json/',
    #          'CORD-19-research-challenge/noncomm_use_subset/noncomm_use_subset/pdf_json/']
    paths = ['CORD-19-research-challenge/comm_use_subset/comm_use_subset/pdf_json/']

    # Getting all files
    id = 1
    for path in paths:
        for file in os.listdir(path):
            # Open the json film corpus
            fullFilePath = path + file

            data = open(fullFilePath)
            currentDoc = json.load(data)
            try:
                abstract = currentDoc['abstract'][0]['text']
            except:
                abstract = ''

            body_text = currentDoc['body_text']

            # ldaModel = LDA(body_text).performLDA()
            documents[str(id)] = [currentDoc['paper_id'], currentDoc['metadata']['title'],
                                  abstract, body_text]
            id = id + 1

    size = len(documents)

    # Action series for bulk loading with helpers.bulk function.
    # Implemented as a generator, to return one document with each call.
    # Note that we include the index name here.
    # The Document type is always 'doc'.
    # Every item to be indexed must have a unique key.
    def actions():
        for mid in range(1, size + 1):
            yield {
                "_index": "covid_19_index",
                "_type": '_doc',
                "_id": documents[str(mid)][0],
                "paper_id": documents[str(mid)][0],
                "title": documents[str(mid)][1],
                "abstract": documents[str(mid)][2],
                "body_text": getBodyText(documents[str(mid)][3])
            }
    helpers.bulk(es, actions())


def getBodyText(body_text):
    all_text = ''
    for text in body_text:
        all_text += text['text']
    return all_text

# command line invocation builds index and prints the running time.
def main():
    start_time = time.time()
    buildIndex()
    print("=== Built index in %s seconds ===" % (time.time() - start_time))


if __name__ == '__main__':
    main()