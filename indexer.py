from parser_module import Parse
import os
import utils
import string

# DO NOT MODIFY CLASS NAME
class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.parser = Parse()
        self.inverted_idx = {}
        self.postingDict = {}
        self.benchDataSet = {}
        self.config = config

        # do for the entities parser rule
        self.onceButTwiceLaterPosting = {}

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        # Get data that needs to be saved
        document_dictionary = document.term_doc_dictionary
        self.benchDataSet[document.tweet_id] = document.term_doc_dictionary

        # Check if the document dictionary isn't empty
        if len(document_dictionary.keys()) != 0:
            maxValueOfWordInDc = max(document_dictionary.values())
            numberOfUniqueWords = len(document_dictionary.keys())
            doc_len = document.doc_length
        else:
            return

        # Go over each term in the doc
        for term in document_dictionary.keys():
            try:
                original_term = term
                capitalTerm = term.upper()
                lowerTerm = term.lower()

                # Check the upper lower case
                if self.first_alfa_upper(term):
                    term = capitalTerm
                    # if exists in dict in capital
                    if capitalTerm in self.inverted_idx.keys():
                        self.inverted_idx[term] +=1
                    # if exists in dict in lower then stay lower
                    elif lowerTerm in self.inverted_idx.keys():
                        term = lowerTerm
                        self.inverted_idx[term] +=1
                    else:
                        # doesn't exist
                        self.inverted_idx[term] = 1
                        self.postingDict[term] = []
                else:
                    # Begins in small letter
                    term = lowerTerm
                    #if until now was capital
                    if capitalTerm in self.inverted_idx.keys():
                        # update in inverted_index dict to lower
                        valueOfCapitalTerms = self.inverted_idx[capitalTerm]
                        del self.inverted_idx[capitalTerm]
                        self.inverted_idx[term] = valueOfCapitalTerms + 1
                        # update in posting to lower
                        if capitalTerm in self.postingDict.keys():
                            value_of_posting = self.postingDict[capitalTerm]
                            del self.postingDict[capitalTerm]
                            self.postingDict[term] = value_of_posting
                    # if saved in lower
                    elif lowerTerm in self.inverted_idx.keys():
                        self.inverted_idx[term] +=1
                    else:
                        # add - didn't exist
                        self.inverted_idx[term] = 1
                        self.postingDict[term] = []

                # update posting dict
                tf = document_dictionary[original_term] / doc_len
                self.postingDict[term].append(
                    (document.tweet_id, document_dictionary[original_term], maxValueOfWordInDc, numberOfUniqueWords,
                     doc_len,tf))

                # # Update inverted index and posting
                # if term not in self.inverted_idx.keys():
                #     self.inverted_idx[term] = 1
                #     self.postingDict[term] = []
                # else:
                #     self.inverted_idx[term] += 1
                #
                # self.postingDict[term].append((document.tweet_id, document_dictionary[term]))

            except:
                print('problem with the following key {}'.format(term[0]))

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        Output:
            inverted_index dictionary, posting dictionary
        """

        return utils.load_obj(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        utils.save_obj(self, fn)

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.postingDict

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else None


    # find if the letter is upper lower
    def first_alfa_upper(self, word):
        for c in word:
            if c.isalpha():
                if c.isupper():
                    return True
                return False
        return False

    def getBenchDataSet(self):
        return self.benchDataSet