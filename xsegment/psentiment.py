#coding=utf-8
#!/usr/bin/env python

from b2.ds2 import DTrie
from b2 import exceptions2
from b2.object2 import singleton
import os


@singleton
class SentimentTrie(object):
    """get document sentiment ; get word sentiment score which measure postive and negative
        Test:
            >>> sentiment = SentimentTrie()
            >>> sentiment.get_word_sentiment('断章取义')
            >>> sentiment.get_word_sentiment('不')
            >>> sentiment.get_words_sentiment(['我' , '喜欢' , '你'])
            >>> sentiment.get_sentence_sentiment(['我' ,'不' , '喜欢' , '你'])
            >>> sentiment.get_sentence_sentiment(['我' , '不' , '恨' , '你'])
    """

    _trie = DTrie()
    __non = set(['不', ' 不是', '没', '几乎不', '从不', '假如'])

    def __init__(self,
                 dict_path=os.path.join(
                     os.path.abspath(os.path.dirname(__file__)),
                     'dict/sentiment_word.txt'),
                 split_word='\t'):
        self.__load(dict_path, split_word)

    def __load(self, dict_path, split_word='\t'):
        with open(dict_path) as f:
            for line in f:
                sentiment_array = line.rstrip().split(split_word)
                if len(sentiment_array) >= 2:
                    self._trie.add(sentiment_array[0], float(
                        sentiment_array[1]))

    def get_word_sentiment(self, word):
        """get word score for postive and negative
        """
        if word is None:
            return None
        if not isinstance(word, bytes):
            exceptions2.raiseTypeError(word)
        find, count, value, error_msg = self._trie.get(word)
        return value if find and isinstance(value, float) else 0.

    def get_words_sentiment(self, word_list=[]):
        """get word array sentiment score
        """
        sentiment_list = []
        if word_list and len(word_list) > 0:
            sentiment_list.extend(
                [(word, self.get_word_sentiment(word)) for word in word_list])
        return sentiment_list

    def get_sentence_sentiment(self, word_list=[]):
        sentiment_point = 0.
        non_num = 0
        for word in word_list:
            if word in self.__non:
                non_num += 1
                continue
            sentiment_point += self.get_word_sentiment(word)
        if non_num % 2 != 0:
            return -sentiment_point
        return sentiment_point
