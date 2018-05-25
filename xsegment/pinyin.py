# coding=utf-8
#!/usr/bin/env python

from b2.ds2 import DTrie
import re
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')


class pinyin():

    __zh = re.compile(ur"([\u4E00-\u9FA5]+)")
    __dict = DTrie()

    def __init__(self,
                 dict_path=os.path.join(
                     os.path.abspath(os.path.dirname(__file__)),
                     'dict/word.data')):
        self.__load(dict_path)

    def __load(self, dict_path):
        with open(dict_path) as f:
            for line in f.readlines():
                pin_yin = line.strip().split('\t')
                if len(pin_yin) == 2:
                    self.__dict.add(pin_yin[0], pin_yin[1])

    def zh2pinyin(self, words, split_word=' '):
        if words is None:
            return ""
        if not isinstance(words, unicode):
            words = words.decode('utf-8')
        result = []
        for word in words:
            p = self.__dict.get('%X' % ord(word))
            if p[-2] is None:
                result.append(word)
            else:
                result.append(p[-2])
        return split_word.join(result)

    def pinyin_segment(self, words, split_word=' '):
        if words:
            if not isinstance(words, unicode):
                words = words.decode('utf-8')
            result = []
            for word in self.__zh.split(words):
                if self.__zh.match(word):
                    result.append(self.zh2pinyin(word.strip(), split_word))
                elif word:
                    result.append('%s' % word.strip())
            return split_word.join(result)
        return ''


if __name__ == "__main__":
    p = pinyin()
    print p.pinyin_segment('12上帝3aa')  #12 shang di 3aa
    print p.pinyin_segment('12上帝3aa', '#')  #  'shang#di#3aa
    print p.zh2pinyin('我爱a')  # wo ai a 不会自动转换不是汉字
    print p.zh2pinyin('我爱a', '#')  # wo#ai#a
