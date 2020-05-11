from tmnt.bow_vae.runtime import BowNTMInference, TextEncoder
import json
import pickle

"""
INSTALL TMNT first within conda env - refer to this link: https://tmnt.readthedocs.io/en/latest/installation.html
this script file will take a list of articles and return its three most related topics 

- pickled file is the generated output - contains one dict: 
    key - document ID 
    value - list of three most probable topics
"""

infer = BowNTMInference('model.params',
                        'model.config',
                        'vocab.json')
text_encoder = TextEncoder(infer)
data_file = open("all_data.json","r")
progress_counter = 0
batch_c = 0 # encoding is processed per 1000
encoding_list = []
encoding_id_list = []
topic_dict = {}
lines = data_file.readlines()

for line in lines:
    document_text = json.loads(line)["text"]
    document_id = json.loads(line)["document_id"]
    encoding_list.append(document_text)
    encoding_id_list.append(document_id)
    batch_c = batch_c + 1
    progress_counter = progress_counter + 1
    if batch_c == 20:
        batch_c = 0
        encoding = text_encoder.encode_batch(encoding_list).asnumpy().tolist()
        for i, each_encoded in enumerate(encoding):
            l = sorted(range(len(each_encoded)), key=lambda x: each_encoded[x])[-2:]
            l.reverse() # a list of two indexes - first element is more probable
            topic_dict[encoding_id_list[i]]= l
        encoding_list = []
        encoding_id_list= []
        print("Total number processed:", progress_counter)

for i, each_encoded in enumerate(encoding):
    l = sorted(range(len(each_encoded)), key=lambda x: each_encoded[x])[-2:]
    l.reverse()  # a list of two indexes - first element is more probable
    topic_dict[encoding_id_list[i]] = l
    print(topic_dict)

# Now generate output pickle
    with open("topic_dict.pkl", 'wb') as f:
        pickle.dump(topic_dict, f)