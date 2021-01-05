

# wordnet search


import csv
import pandas as pd
import search_engine_best
from configuration import ConfigClass
from nltk.corpus import wordnet
from searcher import Searcher

def run_engine():
    # path = "C:\\Users\\omern\\Desktop\\data_part_c\\data\\benchmark_data_train.snappy.parquet"
    path = "data\\benchmark_data_train.snappy.parquet"
    queries_path = "data\\queries_train.tsv"

    config = ConfigClass()
    config.corpusPath = path
    engine = search_engine_best.SearchEngine()
    engine.build_index_from_parquet(path)

    all_queries = query_reader(queries_path)["information_need"]

    for i, q in enumerate(all_queries):
        print(q)
        parsed_q = engine.get_parser().parse_sentence(q)
        k, docs = engine.search(q)
        # print(docs[:10])
        engine.check_engine_quality(i+1, docs[:300])
        print()

    print("Avg map is :", (sum(engine.map_list) / len(engine.map_list)))




def query_reader(queries_path):

    data = pd.read_csv(queries_path, sep="\t")
    return data