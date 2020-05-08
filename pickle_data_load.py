import pickle
import argparse
import json
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)

parser = argparse.ArgumentParser(description='Configuration for loading pickle files')
parser.add_argument('--path', type=str,
                    help='File path to pickle files',
                    default='/Users/jacobhan/Desktop/Brandeis Academic/Spring 2020/COSI 132/proj')
args = parser.parse_args()


def print_this_pickle(pickle_number):
    file_name = args.path + "/" + str(pickle_number) + ".pkl"
    with open(file_name, "rb") as f:
        articles = pickle.load(f) # articles: a dict with paper ID as keys
        for b in articles:
            print (b, articles[b])


def load_into_pandas(pickle_number):
    file_name = args.path + "/" + str(pickle_number) + ".pkl"
    with open(file_name, "rb") as f:
        articles = pickle.load(f) # articles: a dict with paper ID as keys
        df = pd.DataFrame.from_dict(articles)
        df = df.T
        print(df)
        return df


def append_to_pandas_df(pickle_number, dataframe):
    file_name = args.path + "/" + str(pickle_number) + ".pkl"
    with open(file_name, "rb") as f:
        articles = pickle.load(f) # articles: a dict with paper ID as keys
        df = pd.DataFrame.from_dict(articles)
        df = df.T
        dataframe = dataframe.append(df)
        print(dataframe)
        return dataframe


def simple_preprocess(dataframe, column):
    """
    input dataframe and the column of the dataframe to preprocess
    entries within that column must be string

    :return: dataframe with column specified preprocessed
    """
    for each_entry in dataframe[column]:
        idx = dataframe.index[dataframe[column] == each_entry]
        processed_entry = gensim.utils.simple_preprocess(str(each_entry), deacc=True)
        dataframe.at[idx.to_list()[0], column] = processed_entry
    return dataframe


def generate_textual_data(dataframe):
    """
    :param dataframe:
    :return: datdaframe with a new column, textual_data combining text, abstract and title
    """
    textual_data = []
    for index, each_row in dataframe.iterrows():
        this_textual_data = each_row["title"] + each_row["abstract"] + each_row["text"]
        print (this_textual_data)
        textual_data.append(this_textual_data)
    dataframe["textual_data"] = textual_data
    return dataframe


def prep_tmnt(dataframe):
    """

    :param dataframe:
    :return: True if successfully generated JSON files
    """
    train_corpus = []
    val_corpus = []
    test_corpus = []
    split_key = 1  # load into val if split_key is 5; test if split_key is 6
    for index, each_row in dataframe.iterrows():
        text = {"text": each_row["textual_data"]}
        split_key = split_key + 1
        if split_key == 5:
            val_corpus.append(text)
        elif split_key == 6:
            split_key = 0
            test_corpus.append(text)
        else:
            train_corpus.append(text)
    with open('covid_train_data.json', 'w') as wf1:
        wf1.write(
            '' +
            '\n'.join(json.dumps(i) for i in train_corpus) +
            '\n')

    with open('covid_val_data.json', 'w') as wf2:
        wf2.write(
            '' +
            '\n'.join(json.dumps(i) for i in val_corpus) +
            '\n')

    with open('covid_test_data.json', 'w') as wf3:
        wf3.write(
            '' +
            '\n'.join(json.dumps(i) for i in test_corpus) +
            '\n')
    return True

if __name__ == "__main__":
    #print_this_pickle(1)
    df = load_into_pandas(1)
    df  = append_to_pandas_df(2, df)
    df = append_to_pandas_df(3, df)
    df = append_to_pandas_df(4, df)
    df = append_to_pandas_df(5, df)
    df = append_to_pandas_df(6, df)
    df = append_to_pandas_df(7, df)
    df = append_to_pandas_df(8, df)
    df = append_to_pandas_df(9, df)

    # simple preprcoess three columns - title, abstract and text
    # pre = simple_preprocess(df_1, "title")
    # pre = simple_preprocess(pre, "abstract")
    # pre = simple_preprocess(pre, "text")
    # print (pre)

    # insert a new column - textual_data, which is the combination of all three columns
    df_new = generate_textual_data(df)
    print (df_new)
    prep_tmnt(df_new)
    # more pre-processing before feeding to model
