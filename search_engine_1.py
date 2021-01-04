

# wordnet search


import csv
import pandas as pd
import search_engine_best
from configuration import ConfigClass
from searcher import Searcher

def run_engine():
    # path = "C:\\Users\\omern\\Desktop\\data_part_c\\data\\benchmark_data_train.snappy.parquet"
    path = "C:\\Projects\\Python\\data_part_c\\data\\benchmark_data_train.snappy.parquet"
    queries_path = "data\\queries_train.tsv"

    config = ConfigClass()
    config.corpusPath = path
    engine = search_engine_best.SearchEngine()
    engine.build_index_from_parquet(path)

    all_queries = query_reader(queries_path)["information_need"]

    for q in all_queries:
        parsed_q = engine.get_parser().parse_sentence(q)
        engine.search(parsed_q)






def query_reader(queries_path):

    data = pd.read_csv(queries_path, sep="\t")
    return data