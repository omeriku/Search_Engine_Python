#Thesaurus
import statistics

import pandas as pd

import metrics
from reader import ReadFile
from datetime import datetime
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
#from searcher import Searcher
from searcher_Thesaurus import Searcher


# DO NOT CHANGE THE CLASS NAME
class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config)
        self._model = None
        self.map_list = []
        self.prec5_list = []
        self.prec10_list = []
        self.prec50_list = []
        self.prec_total_list = []
        self.recall_list = []
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
        print("\nNow Starting search engine 2")

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


    def run_engine_two(self, fn):

        self.build_index_from_parquet(fn)
        queries_path = "data\\queries_train.tsv"

        all_queries = SearchEngine.query_reader(queries_path)["information_need"]

        for i, q in enumerate(all_queries):
            print(q)
            k, docs = self.search(q)
            # print(docs[:10])
            self.check_engine_quality(i+1, docs[:300])
            print()

        print("Avg map is :", (sum(self.map_list) / len(self.map_list)))

    @staticmethod
    def query_reader(queries_path):

        data = pd.read_csv(queries_path, sep="\t")
        return data


    def get_parser(self):
        return self._parser

    def check_engine_quality(self, query_num, list_of_docs):

        benchmark_path = "data\\benchmark_lbls_train.csv"
        df = pd.read_csv(benchmark_path)

        df_prec = df[df['query'] == query_num]
        df_prec = df_prec[df_prec['tweet'].isin(list_of_docs)]
        dict_for_data = df_prec.set_index('tweet')['y_true'].to_dict()

        rmv_lst = []

        ranking = []
        for doc in list_of_docs:
            try:
                ranking.append(dict_for_data[int(doc)])
            except:
                rmv_lst.append(doc)
        for d in rmv_lst:
            list_of_docs.remove(d)

        data_df = pd.DataFrame({'query': query_num, 'tweet': list_of_docs, 'y_true': ranking})

        df_rec = df[df['query'] == query_num]
        recall_total = len(df_rec[df_rec['y_true'] == 1.0])

        # print("total Relevant doc found with tag 1 :" , len (data_df[data_df['y_true'] == 1.0]))
        # print("total NON relevant doc found with tag 0 :" , len (data_df[data_df['y_true'] == 0]))
        # print("found total of", len(df_prec), "tagged docs")

        prec5 = metrics.precision_at_n(data_df, query_num, 5)
        prec10 = metrics.precision_at_n(data_df, query_num, 10)
        prec50 = metrics.precision_at_n(data_df, query_num, 50)
        prec_total = metrics.precision(data_df, True, query_number=query_num)
        map_of_query = metrics.map(data_df)
        recall_val = metrics.recall_single(data_df, recall_total, query_num)
        self.map_list.append(map_of_query)
        self.prec5_list.append(prec5)
        self.prec10_list.append(prec10)
        self.prec50_list.append(prec50)
        self.prec_total_list.append(prec_total)
        self.recall_list.append(recall_val)

        print()
        print("precision at 5 of query", query_num, "is :", prec5)
        print("precision at 10 of query", query_num, "is :", prec10)
        print("precision at 50 of query", query_num, "is :", prec50)
        print("precision of query", query_num, "is :", prec_total)
        print("recall of query", query_num, "is :", recall_val)
        print("map of query", query_num, "is :", map_of_query)

def main():
    path = "data\\benchmark_data_train.snappy.parquet"
    queries_path = "data\\queries_train.tsv"
    data = pd.read_csv(queries_path, sep="\t")
    all_queries = data["information_need"]

    e = SearchEngine(None)
    e.build_index_from_parquet(path)

    for i, q in enumerate(all_queries):
        print("---- Query Number:", i + 1, "----")
        print(q)
        k, docs = e.search(q)
        # print(docs[:10])
        e.check_engine_quality(i + 1, docs)
        print()
    print("---- Done all queries, now printing statistics ----\n")

    print("Avg map is :", (statistics.mean(e.map_list)))
    print("Avg recall is :", (statistics.mean(e.recall_list)))
    print("Avg precision at 5 is :", (statistics.mean(e.prec5_list)))
    print("Avg precision at 10 is :", (statistics.mean(e.prec10_list)))
    print("Avg precision at 50 is :", (statistics.mean(e.prec50_list)))
    print("Avg precision total is :", (statistics.mean(e.prec_total_list)))

    print()
    print("Median map is :", (statistics.median(e.map_list)))
    print("Median recall is :", (statistics.median(e.recall_list)))
    print("Median precision at 5 is :", (statistics.median(e.prec5_list)))
    print("Median precision at 10 is :", (statistics.median(e.prec10_list)))
    print("Median precision at 50 is :", (statistics.median(e.prec50_list)))
    print("Median precision total is :", (statistics.median(e.prec_total_list)))

    print()
    print("Max map is :", (max(e.map_list)))
    print("Max recall is :", (max(e.recall_list)))
    print("Max precision at 5 is :", (max(e.prec5_list)))
    print("Max precision at 10 is :", (max(e.prec10_list)))
    print("Max precision at 50 is :", (max(e.prec50_list)))
    print("Max precision total is :", (max(e.prec_total_list)))

    print()
    print("Min map is :", (min(e.map_list)))
    print("Min recall is :", (min(e.recall_list)))
    print("Min precision at 5 is :", (min(e.prec5_list)))
    print("Min precision at 10 is :", (min(e.prec10_list)))
    print("Min precision at 50 is :", (min(e.prec50_list)))
    print("Min precision total is :", (min(e.prec_total_list)))

main()


