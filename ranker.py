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
        #dict_Of_CosSimilarity = {}
        listOfTuplesCos = []
        combined = query + wordnet
        # Go over every relevant doc
        for tweetId in relevant_docs:
            sumMone = 0
            term_wijSquare = 0
            query_wiqSquare = 0
            tokensOfDoc = indexer.benchDataSet[tweetId].keys()
            # Go over every token in the tweetId
            for termInDoc in tokensOfDoc:
                # Calculate his wij
                if termInDoc.upper() in indexer.inverted_idx:
                    finalTermInDoc = termInDoc.upper()
                else:
                    finalTermInDoc = termInDoc.lower()


                listOfTerm = indexer.postingDict[finalTermInDoc]

                tf = Ranker.findTF(tweetId, listOfTerm)
                idf = math.log(numOfDocsInCorpus / indexer.inverted_idx[finalTermInDoc], 2)
                wij = tf * idf

                # if the term in wordnet then decrease wij
                if finalTermInDoc in wordnet:
                    wij *= 0.65
                # even if the term is not in the quey them add to mechane
                term_wijSquare += math.pow(wij, 2)

                if finalTermInDoc in combined:
                    sumMone += wij
                    query_wiqSquare += 1

                # wij - tf-idf for each term in eat tweet
                # term_wijSquare = += every wij^2
                # query_wiqSquare = +=1 if the term is in combined
                # sumMone += wij
                # wijSquare += math.pow(wij,2)

            sumMechane = math.sqrt(term_wijSquare * query_wiqSquare)
            if sumMechane == 0:
                cosSimilarity = 0
            else:
                cosSimilarity = sumMone / sumMechane
            #dict_Of_CosSimilarity[tweetId] = cosSimilarity
            cosSimilarity *= (query_wiqSquare / len(query))
            listOfTuplesCos.append((tweetId,cosSimilarity))


        ranked_results = sorted(listOfTuplesCos,key=lambda item:item[1],reverse=True)
        # print()
        # print(ranked_results[:8])
        # print("text1: ",indexer.benchDataSet[ranked_results[0][0]])
        # print("text2: ", indexer.benchDataSet[ranked_results[1][0]])
        # print("text3: ", indexer.benchDataSet[ranked_results[2][0]])
        # print()

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
