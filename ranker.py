# you can change whatever you want in this module, just make sure it doesn't 
# break the searcher module
import math


class Ranker:
    def __init__(self):
        pass

    @staticmethod
    def rank_relevant_docs(query, related_terms, relevant_docs, indexer, k=None):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param indexer:
        :param related_terms:
        :param query:
        :param k: number of most relevant docs to return, default to everything.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        numOfDocsInCorpus = len(indexer.benchDataSet)
        listOfTuplesCos = []
        combined = query + related_terms
        # Go over every relevant doc

        # wij - tf-idf for each term in eat tweet
        # term_wijSquare = += every wij^2
        # query_wiqSquare = +=1 if the term is in combined
        # sumMone += wij
        # wijSquare += math.pow(wij,2)

        for tweetId in relevant_docs:
            sumMone = 0
            term_wijSquare = 0
            query_wiqSquare = 0
            wordnet_counter = 0
            tokensOfDoc = indexer.benchDataSet[tweetId]
            # Go over every token in the tweetId
            for termInDoc in tokensOfDoc:
                # Calculate his wij
                if termInDoc.upper() in indexer.inverted_idx:
                    finalTermInDoc = termInDoc.upper()
                else:
                    finalTermInDoc = termInDoc.lower()

                try:
                    listOfTerm = indexer.postingDict[finalTermInDoc]

                    tf = Ranker.findTF(tweetId, listOfTerm)
                    idf = math.log(numOfDocsInCorpus / indexer.inverted_idx[finalTermInDoc], 2)
                    wij = tf * idf

                    # even if the term is not in the quey them add to mechane
                    term_wijSquare += math.pow(wij, 2)

                except:
                    continue

                # even if the term is not in the quey them add to mechane
                if finalTermInDoc in combined:
                    # if the term in wordnet then decrease wij
                    if finalTermInDoc in related_terms:
                        wij *= 0.85
                        wordnet_counter += 1
                    sumMone += wij
                    query_wiqSquare += 1

            sumMechane = math.sqrt(term_wijSquare * query_wiqSquare)
            if sumMechane == 0:
                cosSimilarity = 0
            else:
                cosSimilarity = sumMone / sumMechane

            if len(related_terms) > 0:
                wordnet_factor = (wordnet_counter / len(related_terms))
            else:
                wordnet_factor = 0
            cosSimilarity = 0.7 * cosSimilarity + 0.3 * sumMone
            cosSimilarity *= ( (query_wiqSquare / len(query)) + wordnet_factor)
            listOfTuplesCos.append((tweetId, cosSimilarity))

        ranked_results = sorted(listOfTuplesCos,key=lambda item:item[1],reverse=True)

        if k is not None:
            ranked_results = ranked_results[:k]

        return [d[0] for d in ranked_results]

    @staticmethod
    def findTF(tweetId, listOfDocs):
        # Find tf value of term in doc
        for doc in listOfDocs:
            if doc[0] == tweetId:
                return doc[5]
