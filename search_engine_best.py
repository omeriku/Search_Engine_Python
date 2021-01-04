import pandas as pd
from reader import ReadFile
from datetime import datetime
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils
import statistics

# DO NOT CHANGE THE CLASS NAME
class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config)
        self._model = None

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """
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
        self._indexer.save_index("idx_bench")
        # cutter = statistics.mean(self._indexer.inverted_idx.values())
        # cutter = sorted(self._indexer.inverted_idx.values(), reverse=True)[int(len(self._indexer.inverted_idx) * 0.2)]
        # print("cut from value of: ", cutter)
        # print("Total Tweets :", number_of_documents)
        # sorted_dic = {key: value for key, value in sorted(self._indexer.inverted_idx.items(), key=lambda item: item[1], reverse=True) if key.__contains__(".com")}
        # print("sorted =",len(sorted_dic))
        # print(sorted_dic)
        print('Finished parsing and indexing.')

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self._indexer.load_index(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and 
        assign to self._model, which is passed on to the searcher at query time.
        """
        pass

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
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


def main():
    # path = "C:\\Users\\omern\\Desktop\\data_part_c\\data\\benchmark_data_train.snappy.parquet"
    path = "C:\\Projects\\Python\\data_part_c\\data\\benchmark_data_train.snappy.parquet"
    config = ConfigClass()
    config.corpusPath = path
    search = SearchEngine()
    search.build_index_from_parquet(path)

