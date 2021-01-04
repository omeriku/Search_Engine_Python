from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document


class Parse:

    def __init__(self):
        self.stop_words = frozenset(stopwords.words('english'))

    def parse_sentence(self, text, stemming = False):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        text_tokens = word_tokenize(text)
        tokenized_text_with_rules = self.parser_rules(text_tokens, stemming)
        # text_tokens_without_stopwords = [w.lower() for w in text_tokens if w not in self.stop_words]
        return tokenized_text_with_rules

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-presenting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        try:
            indice = doc_as_list[4]
            retweet_text = doc_as_list[5]
            retweet_url = doc_as_list[6]
            retweet_indice = doc_as_list[7]
            quote_text = doc_as_list[8]
            quote_url = doc_as_list[9]

        except:
            retweet_text = doc_as_list[4]
            retweet_url = doc_as_list[5]
            quote_text = doc_as_list[6]
            quote_url = doc_as_list[7]

        term_dict = {}

        if len(url) > 2:
            full_text += url
        tokenized_text = self.parse_sentence(full_text)

        doc_length = len(tokenized_text)  # after text operations.

        for term in tokenized_text:
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)
        return document



    def parser_rules(self, token_text, stemming=False):
        rmv = []
        add = []
        url_stop = ["/", "\\", "-", "=", '%', "'", " ", ":", "`", '``', '_', '"', "...", '``', "''"]
        nameOrEntity = ""
        counterOfCapitalInARow = 0

        for i, token in enumerate(token_text):

            if token in self.stop_words or token.lower() in self.stop_words or token in url_stop:
                rmv.append(token)
                continue
            # Check for unwanted chars like : . ; , / etc
            if len(token) == 1 and token not in ["@", "#", "$"]:
                # if ord(token_text[i]) > 122 or 90 < ord(token_text[i]) < 97 or 57 < ord(token_text[i]) < 64 or 37 < ord(token_text[i]) < 48 or 31 < ord(token_text[i]) < 35:
                rmv.append(token_text[i])
                continue
            # Remove unwanted expressions
            if token.__contains__("t.co") or token.__contains__("http") or token.lower() == "rt" or token.__contains__("twitter.com"):
                rmv.append(token)
                continue
            # url detector
            if token.__contains__("//"):
                word = ""
                for c in token_text[i]:
                    if c in url_stop or (c == "." and word.__contains__("www")):
                        if word not in url_stop:
                            add.append(word)
                        word = ""
                    else:
                        word += c
                rmv.append(token)
                add.append(word)
                continue

            # Check if it is a tag
            if token_text[i] == "@" and i < len(token_text)-1:
                token_text[i] = token_text[i] + token_text[i+1]
                rmv.append(token_text[i+1])
                continue
            # Check if it is a hashtag and analyze the hashtag to words according to Upper letters
            if token_text[i] == "#" and i < len(token_text)-1:
                token_text[i] = token_text[i] + token_text[i+1]
                rmv.append(token_text[i+1])
                add = self.word_cutter(add, url_stop, token_text[i+1])
                continue
            # Turn every context of dollars to the word dollar
            if token.lower() in ["$", "dollars"]:
                token_text[i] = "dollar"
                continue

            # Turn every context of percentage to %
            if self.is_real_number(token_text[i]) and i < len(token_text) - 1:
                if token_text[i+1].lower() in ["%", "percentage", "percent"]:
                    token_text[i] = token_text[i] + "%"
                    rmv.append(token_text[i + 1])
                    continue

            # Names and Entities - will be 2 or 3 tokens
            if token_text[i][0].isupper() and counterOfCapitalInARow < 3 and not token_text[i].isnumeric():
                nameOrEntity = nameOrEntity + " " + token_text[i]
                # delete space in the beginning
                if counterOfCapitalInARow == 0:
                    nameOrEntity = nameOrEntity[1:len(nameOrEntity)]
                counterOfCapitalInARow += 1
            elif 1 < counterOfCapitalInARow < 4: # add to the right set - number of times that the entity exists so far

                add.append(nameOrEntity.upper())
                nameOrEntity = ""
                counterOfCapitalInARow = 0
            else:
                nameOrEntity = ""
                counterOfCapitalInARow = 0

            # Check if it is a big number
            if self.is_real_number_comma(token_text[i]):
                try:
                    # Convert to float and int
                    convertedNumToFloat = float(token_text[i].replace(',', ''))
                    convertedToInt = int(convertedNumToFloat)
                    # The final number
                    if convertedToInt == convertedNumToFloat:
                        finalNumber = convertedToInt
                    else:
                        finalNumber = convertedNumToFloat

                    # Check if the next token is thousand, million, billion or fraction
                    if finalNumber < 1000:
                        if i < len(token_text) - 1 and token_text[i + 1] in ["Thousand", "thousand", "Thousands", "thousands"]:
                            convertedToString = str(finalNumber) + "K"

                        elif i < len(token_text) - 1 and token_text[i + 1] in ["Million", "million", "Millions", "millions"]:
                            convertedToString = str(finalNumber) + "M"

                        elif i < len(token_text) - 1 and token_text[i + 1] in ["Billion", "billion", "Billions", "billions"]:
                            convertedToString = str(finalNumber) + "B"

                        # if the next token is fraction then connect them
                        elif i + 1 < len(token_text) and self.is_fraction(token_text[i + 1]):
                            convertedToString = token_text[i] + " " + token_text[i + 1]
                        else:
                            continue

                        # Add to lists
                        add.append(convertedToString)
                        rmv.append(token_text[i])
                        rmv.append(token_text[i + 1])

                    # if it is a thousand number
                    elif 999 < convertedToInt < 999999:
                        finalNumber /= 1000

                        # After division need to save again 1 or 1.0 for example
                        convertedNumToFloat = float(finalNumber)
                        convertedToInt = int(convertedNumToFloat)
                        if convertedToInt == convertedNumToFloat:
                            finalNumber = convertedToInt
                        else:
                            finalNumber = convertedNumToFloat
                            finalNumber = self.round_down(finalNumber)

                        convertedToString = str(finalNumber) + "K"

                        # Add to lists
                        add.append(convertedToString)
                        rmv.append(token_text[i])

                    # if it is a Million number
                    elif 999999 < convertedToInt <= 999999999:
                        finalNumber /= 1000000

                        # After division need to save again 1 or 1.0 for example
                        convertedNumToFloat = float(finalNumber)
                        convertedToInt = int(convertedNumToFloat)
                        if convertedToInt == convertedNumToFloat:
                            finalNumber = convertedToInt
                        else:
                            finalNumber = convertedNumToFloat
                            finalNumber = self.round_down(finalNumber)

                        convertedToString = str(finalNumber) + "M"

                        # Add to lists
                        add.append(convertedToString)
                        rmv.append(token_text[i])

                    # if it is a Billion number
                    elif 9999999 < convertedToInt:
                        finalNumber /= 1000000000

                        # After division need to save again 1 or 1.0 for example
                        convertedNumToFloat = float(finalNumber)
                        convertedToInt = int(convertedNumToFloat)
                        if convertedToInt == convertedNumToFloat:
                            finalNumber = convertedToInt
                        else:
                            finalNumber = convertedNumToFloat
                            finalNumber = self.round_down(finalNumber)

                        convertedToString = str(finalNumber) + "B"
                        # Add to lists
                        add.append(convertedToString)
                        rmv.append(token_text[i])
                except:
                    continue

            # Split words that will mean something after splitting
            if any(one_char in url_stop+["."] for one_char in token_text[i]):
                # print(token_text[i])
                word = ""
                for c in token_text[i]:
                    if c in url_stop+["."]:
                        if word not in add:
                            add.append(word)
                        word = ""
                    elif c.isdigit():
                        if word.isnumeric():
                            word += c
                        else:
                            if word not in add:
                                add.append(word)
                            word = c
                    else:
                        word += c
                if word not in add:
                    add.append(word)
                rmv.append(token_text[i])
                continue


        for w in rmv:
            if w in token_text:
                token_text.remove(w)
        for w2 in add:
            if w2 == "" or w2 in url_stop:
                continue
            token_text.append(w2)
        # Stem if asked
        if stemming:
            s = Stemmer()
            for i, token in enumerate(token_text):
                if self.first_alfa_upper(token):
                    token_text[i] = s.stem_term(token).upper()
                else:
                    token_text[i] = s.stem_term(token)

        return token_text

    def is_real_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def is_real_number_comma(self, s):
        if s in ["Infinity", "infinity", "Nan", "NaN", "NAN", "nan", "nAn", "nAN", "naN"]:
            return False
        try:
            float(s.replace(',', ''))
            return True
        except ValueError:
            return False

    def is_fraction(self, token):
        # Check if the structure is digits/digits
        saveIndex = -1
        for i in range(len(token)):
            if token[i].isdigit():
                continue
            if token[i] == '/' and i != 0:
                # save index for the rest of the fraction
                saveIndex = len(token) - i
                break
            return False
        if saveIndex == -1:
            return False
        for j in range(len(token) - saveIndex):
            if not token[j].isdigit():
                return False
        return True

    # do the round down - from 1010.56 to 1.01K/M/B
    def round_down(self, numToken):
        strNumToken = str(numToken)
        # if int number
        if '.' not in strNumToken:
            return numToken
        else:
            beforeAndAfterString = strNumToken.split('.')
            # Take whole part of the int and just part of the fraction number
            if len(beforeAndAfterString[1]) > 3:
                beforeAndAfterString[1] = beforeAndAfterString[1][0:3]
                toReturn = beforeAndAfterString[0] + "." + beforeAndAfterString[1]
            else:
                toReturn = beforeAndAfterString[0] + "." + beforeAndAfterString[1]
            # Remove 0 at the last of the string
            lengthOfAfterPoint = len(beforeAndAfterString[1])
            while lengthOfAfterPoint != 0 and toReturn[len(toReturn)-1] == '0':
                if toReturn[len(toReturn)-1] == '0':
                    toReturn = toReturn[:len(toReturn)-1]
                lengthOfAfterPoint -= 1
                beforeAndAfterString[1] = beforeAndAfterString[1][:lengthOfAfterPoint]

            if toReturn[len(toReturn) - 1] == '.':
                toReturn = toReturn[:len(toReturn) - 1]

        return toReturn

    def isContainsDigit(self, term):
        for ch in term:
            if ch.isdigit():
                return True
        return False

    def word_cutter(self, add, url_stop, original_word):
        word = ""
        if original_word.isupper():
            for c in original_word:
                if c.isupper():
                    word += c
                elif c.isdigit():
                    if word.isnumeric():
                        word += c
                    else:
                        add.append(word)
                        word = c
        else:
            for c in original_word:
                if c in url_stop:
                    add.append(word)
                    word = ""
                    continue
                if c.isupper():
                    add.append(word)
                    word = c
                elif c.isdigit():
                    if word.isnumeric():
                        word += c
                    else:
                        add.append(word)
                        word = c
                else:
                    word += c
        add.append(word)

        return add

    def first_alfa_upper(self, word):
        for c in word:
            if c.isalpha():
                if c.isupper():
                    return True
                return False
        return False
