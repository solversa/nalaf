import abc
from nltk.tokenize import word_tokenize
from structures.data import Token


class Tokenizer():
    @abc.abstractmethod
    def tokenize(self, dataset):
        return


class NLTKTokenizer(Tokenizer):
    def tokenize(self, dataset):
        for part in dataset.parts():
                part.sentences = [[Token(word) for word in word_tokenize(sentence)] for sentence in part.sentences]