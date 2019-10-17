import json
import math
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from bs4 import BeautifulSoup
from pymongo import MongoClient


class Milestone:

    def __init__(self, file_name):
        self.j_file = file_name
        self.folders = []
        self.count = 0
        self.token_count = 0

    def readFile(self):
        with open(self.j_file) as file:
            try:
                data = json.load(file)
            except ValueError:
                data = {}

        for i in data:
            self.count = self.count + 1
            self.folders.append(i)

    def tokenize(self, link):
        stop_words = set(stopwords.words('english'))
        tokenizer = RegexpTokenizer(r'\w+')
        words = {}
        body = ""
        title = ""
        head1 = ""
        head2 = ""
        data = open(link, encoding="utf8").read()
        soup = BeautifulSoup(data, "lxml")

        for text in soup.find_all("html"):
            body = text.text + body + " "

        for text in soup.find_all("title"):
            title = text.text + title + " "

        for text in soup.find_all("h1"):
            head1 = text.text + head1 + " "

        for text in soup.find_all("h2"):
            head2 = text.text + head2 + " "

        tokens = tokenizer.tokenize((body))
        for token in tokens:
            if token not in stop_words:
                if token.lower() not in words:
                    words.update({token.lower(): 1})
                else:
                    words[token.lower()] += 1

        tokens = tokenizer.tokenize((title))
        for token in tokens:
            if token not in stop_words:
                if token.lower() not in words:
                    words.update({token.lower(): 1})
                else:
                    words[token.lower()] += 2

        tokens = tokenizer.tokenize((head1))
        for token in tokens:
            if token not in stop_words:
                if token.lower() not in words:
                    words.update({token.lower(): 1})
                else:
                    words[token.lower()] += 2

        tokens = tokenizer.tokenize((head2))
        for token in tokens:
            if token not in stop_words:
                if token.lower() not in words:
                    words.update({token.lower(): 1})
                else:
                    words[token.lower()] += 2
        return words



    def normalization(self, words):
        denominator = 0
        for word in words:
            words[word] = 1 + math.log(words[word], 10)
            denominator += words[word] * words[word]
        denominator = math.sqrt(denominator)
        for word in words:
            words[word] = words[word]/denominator
        return words

    def indexing(self):
        indextable = {}
        for link in self.folders:
            freq = self.tokenize(link)
            words = self.normalization(freq)
            for word in words:
                link_tuple = (link, words[word])
                if word in indextable:
                    indextable[word].append(link_tuple)
                else:
                    indextable[word] = []
                    indextable[word].append(link_tuple)
                    self.token_count += 1
        #print((self.token_count))
        return indextable

    def writeToMDB(self, table):
        try:
            conn = MongoClient()
            print("Connected successfully!!!")
        except:
            print("Could not connect to MongoDB")



if __name__ == "__main__":
    index = Milestone("bookkeeping.json")
    index.readFile()
    table = index.indexing()
    print(json.dumps(table, indent=2))




