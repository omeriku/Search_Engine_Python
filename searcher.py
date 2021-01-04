from ranker import Ranker
from nltk.corpus import wordnet
import utils
from indexer import Indexer


# DO NOT MODIFY CLASS NAME
class Searcher:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model 
    # parameter allows you to pass in a precomputed model that is already in 
    # memory for the searcher to use such as LSI, LDA, Word2vec models. 
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None):
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
        query_as_list = self._parser.parse_sentence(query)
        q_wordnet = self.do_wordnet(query_as_list)

        self.upper_lower_case(query_as_list, self._indexer)
        self.upper_lower_case(q_wordnet, self._indexer)

        print("query as list: ", query_as_list)
        print("wordnet :", q_wordnet)

        relevant_docs = self._relevant_docs_from_posting(query_as_list)
        n_relevant = len(relevant_docs)
        ranked_doc_ids = Ranker.rank_relevant_docs(query_as_list, q_wordnet, relevant_docs, self._indexer, k) # @Todo add omer code
        return n_relevant, ranked_doc_ids

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """

        relevant_docs = {}
        # Go over every term in the query
        for term in query_as_list:
            posting_list = self._indexer.get_term_posting_list(term)

            # Check if the term exists in the corpus
            if posting_list is None:
                continue
            # Go over every doc that has the term
            for doc in posting_list:
                docId = doc[0]
                if docId not in relevant_docs:
                    relevant_docs[docId] = 1
                else:
                    relevant_docs[docId] += 1
        return relevant_docs

    @staticmethod
    def do_wordnet(query):
        unique = set()
        lowered = []
        for word in query:
            lowered.append(word.lower())

        for word in lowered:
            for dup in wordnet.synsets(word):
                if dup.lemmas()[0].name().__contains__("_"):
                    all = dup.lemmas()[0].name().split("_")
                    for name in all:
                        if name.lower() not in lowered:
                            unique.add(name.lower())
                else:
                    name = dup.lemmas()[0].name().lower()
                    if name.lower() not in lowered:
                        unique.add(name)

        return list(unique)

    @staticmethod
    def upper_lower_case(list_of_words, indexer):
        for i, w in enumerate(list_of_words):
            if w.lower() in indexer.inverted_idx:
                list_of_words[i] = w.lower()
            elif w.upper() in indexer.inverted_idx:
                list_of_words[i] = w.upper()
        # @Todo what with words that not in inverted

