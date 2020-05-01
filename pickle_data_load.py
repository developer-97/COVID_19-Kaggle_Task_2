import pickle
import argparse

parser = argparse.ArgumentParser(description='Configuration for loading pickle files')
parser.add_argument('--path', type=str,
                    help='File path to pickle files',
                    default='/Users/jacobhan/Desktop/Brandeis Academic/Spring 2020/COSI 132/proj')
args = parser.parse_args()

def print_this_pickle(pickle_number):
    file_name = args.path + "/" + str(pickle_number) + ".pkl"
    with open(file_name, "rb") as f:
        articles = pickle.load(f)
        print(articles)

if __name__ == "__main__":
    print_this_pickle(1)