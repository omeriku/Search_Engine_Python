

# wordnet search


import csv
from datetime import datetime

import pandas as pd
import search_engine_best
from configuration import ConfigClass
from nltk.corpus import wordnet

from indexer import Indexer
from parser_module import Parse
from searcher import Searcher


class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config)
        self._model = None
        self.map_list = []

    def build_index_from_parquet(self, fn):
        print("\nNow Starting search engine 1")

        total_time = datetime.now()
        df = pd.read_parquet(fn, engine="pyarrow")
        documents_list = df.values.tolist()
        # Iterate over every document in the file
        number_of_documents = 0
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)
            number_of_documents += 1
            # index the document data
            self._indexer.add_new_doc(parsed_document)
        print("len of inverted: ", len(self._indexer.inverted_idx))
        print("len of posting: ", len(self._indexer.postingDict))
        print("len of dataSet: ", len(self._indexer.benchDataSet))
        end_time = datetime.now()
        print('\n ------ Time To Retrieve: {}'.format(end_time - total_time), " ------\n")
        print('Finished parsing and indexing.')


    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and
        assign to self._model, which is passed on to the searcher at query time.
        """
        pass

    def search(self, query):
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        return searcher.search(query)

    def get_parser(self):
        return self._parser


    @staticmethod
    def run_engine(fn):
        path = fn
        queries_path = "data\\queries_train.tsv"

        config = ConfigClass()
        config.corpusPath = path
        engine = search_engine_best.SearchEngine()
        engine.build_index_from_parquet(path)

        # all_queries = SearchEngine.query_reader(queries_path)["information_need"]
        #
        # for i, q in enumerate(all_queries):
        #     print(q)
        #     parsed_q = engine.get_parser().parse_sentence(q)
        #     k, docs = engine.search(q)
        #     # print(docs[:10])
        #     engine.check_engine_quality(i+1, docs[:300])
        #     print()
        #
        # print("Avg map is :", (sum(engine.map_list) / len(engine.map_list)))



    @staticmethod
    def query_reader(queries_path):

        data = pd.read_csv(queries_path, sep="\t")
        return data