import json
import re
import sys
import time
import os
from datetime import datetime
#from LDA import LDA

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch_dsl import Index, Document, Text, Integer
from elasticsearch_dsl.analysis import tokenizer, analyzer
from elasticsearch_dsl.connections import connections

# Connect to local host server
connections.create_connection(hosts=['127.0.0.1'])

# Create elasticsearch object
es = Elasticsearch()

# Define analyzers appropriate for your data.
# You can create a custom analyzer by choosing among elasticsearch options
# or writing your own functions.
# Elasticsearch also has default analyzers that might be appropriate.

semi_colon_tokenizer = tokenizer(type='pattern', pattern=';',
                                 name_or_instance='semi_colon_tokenizer')

my_analyzer = analyzer('custom',
                       tokenizer='standard',
                       filter=['lowercase', 'stop', 'porter_stem']
                       )

author_analyzer = analyzer('standard',
                           tokenizer=semi_colon_tokenizer,
                           filter=['stop']
                           )

# Define document mapping (schema) by defining a class as a subclass of Document.
# This defines fields and their properties (type and analysis applied).
# You can use existing es analyzers or use ones you define yourself as above.
class Document_COVID_19(Document):
    # sha = Text(analyzer='simple')
    title = Text(analyzer=my_analyzer)
    # abstract = Text(analyzer=my_analyzer)
    # authors = Text(analyzer=author_analyzer)
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
    path = 'pdf_json'
    #Getting all files
    id = 1
    for file in os.listdir(path):
        # Open the json film corpus
        # with open('CORD-19-research-challenge/comm_use_subset/comm_use_subset/pdf_json/'+str(file), 'r', encoding='utf-8') as data_file:
        fullFilePath = '/Users/jasmynejeanremy/Desktop/COVID_19-Kaggle_Task_2/pdf_json/'+file
        
        
        data = open(fullFilePath)
        currentDoc = json.load(data)
        try:
            abstract = currentDoc['abstract'][0]['text']
        except:
            abstract = ''

        body_text = currentDoc['body_text']

        
        
        #ldaModel = LDA(body_text).performLDA()
        documents[str(id)] = [currentDoc['paper_id'],currentDoc['metadata']['title'],
                              abstract, body_text]
        id = id + 1
        

    size = len(documents)
    # Action series for bulk loading with helpers.bulk function.
    # Implemented as a generator, to return one movie with each call.
    # Note that we include the index name here.
    # The Document type is always 'doc'.
    # Every item to be indexed must have a unique key.
    print(size)
    def actions():
        # mid is movie id (used as key into movies dictionary)
        for mid in range(1, size + 1):
            yield {
                "_index": "covid_19_index",
                "_type": '_doc',
                "paper_id": documents[str(mid)][0],
                "title": documents[str(mid)][1],
                "abstract": documents[str(mid)][2],
                "body_text": getBodyText(documents[str(mid)][3])
                # "sha": documents[str(mid)]['sha'],
                # "title": documents[str(mid)]['title'],
                # "abstract": stringBytesLimit(documents[str(mid)]['abstract']),
                # "authors": str(documents[str(mid)]['authors']).replace(",",""),
                # "publish_time": publish_time_converter(documents[str(mid)]['publish_time'])
            }
    helpers.bulk(es, actions())

def getBodyText(body_text):
    all_text=''
    for text in body_text:
        all_text+=text['text']
    return all_text
"""
Converts publish_time string into an integer
"""
def publish_time_converter(publish_time):
    try:
        if len(publish_time)==4:
            return datetime.strptime(publish_time,'%Y').timestamp()
        elif '-' in publish_time:
            return datetime.strptime(publish_time.split('-')[0],'%Y %b').timestamp()
        elif len(publish_time.split(' '))==2:
            return datetime.strptime(publish_time,'%Y %b').timestamp()
        else:
            return datetime.strptime(publish_time,'%Y %b %d').timestamp()
    except ValueError:
        year = re.match('.*([1-3][0-9]{3})', publish_time).group(0)
        if year is not None:
            return datetime.strptime(year,'%Y').timestamp()
        else:
            return sys.maxsize

"""
Ensures abstract is not over the allowed byte limit for an entry
"""
def stringBytesLimit(abstract):
    return "".join([chr(byte) for byte in str.encode(abstract)[0:32764]])


# command line invocation builds index and prints the running time.
def main():
    start_time = time.time()
    buildIndex()
    print("=== Built index in %s seconds ===" % (time.time() - start_time))


if __name__ == '__main__':
    main()