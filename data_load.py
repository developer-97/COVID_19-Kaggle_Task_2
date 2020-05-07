import json
import os
import pickle
import argparse

parser = argparse.ArgumentParser(description='Configuration')
parser.add_argument('--path', type=str,
                    help='File path to COVID-19 dataset',
                    default='/Users/jacobhan/Downloads/CORD-19-research-challenge/comm_use_subset')
parser.add_argument('--batch', type=int, help='Amount of articles in a single pickle file',
                    default=2000)
args = parser.parse_args()

def all_json_file_path():
    paths = []
    for (root,dirs,files) in os.walk(args.path):
        for x in files:
            if x.endswith(".json"):
                this_path = os.path.join(root, x)
                paths.append(this_path)
    return paths

def load_this_article(path, articles_dict):
    """
    load json file article into the dictionary; titles, authors and text
    the key for each article is its ID

    :param path: path to this JSON object, fetched from list
    :param articles_dict: the dict to put the output into
    :return: none
    """
    with open(path, 'r') as f:
        article = json.load(f)
        this_article_dict = {}
        body_text = ""
        abstract_text =""
        for text in article['body_text']:
            body_text = body_text + text['text']
        try:
            for text in article['abstract']:
                abstract_text = abstract_text + text['text']
        except KeyError:
            pass
        this_article_dict["title"] = article["metadata"]["title"]
        this_article_dict["text"] = body_text
        this_article_dict["abstract"] = abstract_text
        this_article_dict["authors"] = article["metadata"]["authors"]
        print (this_article_dict)
        print("---------------------")

        this_article_id = article["paper_id"]
        articles_dict[this_article_id] = this_article_dict


def generate_output(articles_dict, batch_count):
    file_name = str(batch_count) + ".pkl"
    with open(file_name, 'wb') as f:
        pickle.dump(articles_dict, f)

if __name__ == "__main__":
    file_paths = all_json_file_path()
    count = 1
    this_batch = 1
    articles_dict = {}
    for file in file_paths:
        if count > args.batch:
            generate_output(articles_dict, this_batch)
            count = 1
            this_batch = this_batch + 1
            articles_dict.clear()
            print("Current Count:", count, "  Batch:", this_batch)
            load_this_article(file, articles_dict)
        else:
            print("Current Count:", count, "  Batch:", this_batch)
            load_this_article(file, articles_dict)
        # if count == 5:
        #     generate_output(articles_dict, this_batch)
        #     break
        count = count + 1