# you can change whatever you want in this module, just make sure it doesn't 
# break the searcher module
import math


class Ranker:
    def __init__(self):
        pass

    @staticmethod
    def rank_relevant_docs(query,wordnet,relevant_docs, indexer, k=None):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param k: number of most relevant docs to return, default to everything.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        numOfDocsInCorpus = len(indexer.benchDataSet)
        dict_Of_CosSimilarity = {}
        listOfTuplesCos = []
        combined = query + wordnet
        # Go over every relevant doc
        for tweetId in relevant_docs:
            sumMone = 0
            wijSquare = 0
            wiqSquare=0
            tokensOfDoc = indexer.benchDataSet[tweetId]
            # Go over every term that is relevant to the query
            for term in combined:
                # if the term is not in the tweet_id
                if term not in tokensOfDoc:
                    continue
                wiqSquare += 1
                tf = Ranker.findTF(tweetId,indexer.postingDict[term])
                idf = math.log(numOfDocsInCorpus / indexer.inverted_idx[term],2)
                wij = tf * idf

                if term in wordnet:
                    wij *= 0.65
                sumMone += wij
                wijSquare += math.pow(wij,2)

            sumMechane = math.sqrt(wijSquare * wiqSquare)
            if sumMechane == 0:
                cosSimilarity = 0
            else:
                cosSimilarity = sumMone / sumMechane
            dict_Of_CosSimilarity[tweetId] = cosSimilarity
            listOfTuplesCos.append((tweetId,cosSimilarity))

        ranked_results = sorted(listOfTuplesCos,key=lambda item:item[1],reverse=True)
        #ranked_results = sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True)
        if k is not None:
            ranked_results = ranked_results[:k]
        x=[d[0] for d in ranked_results]
        return [d[0] for d in ranked_results]


    @staticmethod
    def findTF(tweetId,listOfDocs):
        # Find tf value of term in doc
        for doc in listOfDocs:
            if doc[0] == tweetId:
                return doc[5]