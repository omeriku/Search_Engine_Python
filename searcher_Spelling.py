# spelling
#from autocorrect import Speller
from spellchecker import SpellChecker
from ranker import Ranker

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
        q_new_spelling, wrongWords = self.do_spelling(query_as_list)
        # print("query_as_list: ", query_as_list)
        # print("q_new_spelling: ", q_new_spelling)
        # print("wrongWords: ", wrongWords)
        query_as_list = self.deleteWrongSpelledWords(query_as_list,wrongWords)

        self.upper_lower_case(query_as_list, self._indexer)
        self.upper_lower_case(q_new_spelling, self._indexer)
        self.upper_lower_case(wrongWords, self._indexer)


        # print("query as list: ", query_as_list)
        # print("wordnet :", q_wordnet)
        # Find relevant docs
        relevant_docs = self._relevant_docs_from_posting(query_as_list + q_new_spelling + wrongWords)
        n_relevant = len(relevant_docs)
        # Send all to ranking
        ranked_doc_ids = Ranker.rank_relevant_docs(query_as_list + q_new_spelling ,wrongWords, relevant_docs, self._indexer, k)
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
    def upper_lower_case(list_of_words, indexer):
        for i, w in enumerate(list_of_words):
            if w.lower() in indexer.inverted_idx:
                list_of_words[i] = w.lower()
            elif w.upper() in indexer.inverted_idx:
                list_of_words[i] = w.upper()

    @staticmethod
    def do_spelling(query):
        nowSpelled = []
        toDeleteFromQuery = []

        spell = SpellChecker()


        # check spelling of each word
        for word in query:

            afterSpelling = spell.correction(word)

            # if it was a wrong spelling
            if afterSpelling != word:
                # its a new word now right
                nowSpelled.append(afterSpelling)
                # not spelled right
                toDeleteFromQuery.append(word)

        return nowSpelled,toDeleteFromQuery

    # Delete from original query the words that were spelled wrong
    @staticmethod
    def deleteWrongSpelledWords(query, wrongWords):
        newQuery = []
        # for each word in the query
        for term in query:
            # if one of them was spelled wrong
            if term not in wrongWords:
                newQuery.append(term)
        return newQuery



