# coding=utf-8
#!/usr/bin/env python


import re
from collections import defaultdict
import math

split = re.compile("\\s+", re.I).split
chinese = re.compile(ur"[\u4e00-\u9fa5]{2,}").match


class TextRank(object):

    split_regx = re.compile('\\s+').split

    def __init__(self):
        pass

    def extractWord(self, sententce):
        '''
        关键词抽取 ：
        textrank 算法实现
        '''
        if sententce and len(sententce) > 0:
            if isinstance(sententce, (str, unicode)):
                sententce = self.split_regx(sententce)
            elif not isinstance(sententce, (list, tuple)):
                raise Exception, 'type erro'
        sententce = [
            word for word in sententce if chinese(word.decode('utf-8'))]
        word_map = self.__create_word_map(sententce)
        word_len = len(set(word_map))  # 词数
        word_arry = TextRank.createList(word_len, word_len)
        for i in range(1, len(sententce)):
                # 建立窗口 ， 一个词投给另个词
            word_arry[word_map[sententce[i]]][word_map[sententce[i - 1]]] += 1
        score = self.dopagerank(word_arry)
        text_rank = [(__key, score[__val])
                     for __key, __val in word_map.items()]
        return sorted(text_rank, key=lambda x: x[1], reverse=True)

    def dopagerank(self, word_arry, iter=30, d=0.85, diff=0.0001):
        max_diff = 0.
        score = [0.1 for _ in range(len(word_arry))]
        score_back = [0.1 for _ in range(len(word_arry))]
        for count in range(iter):
            for c in range(len(score)):
                score_back[c] = score[c]
            for i in range(len(word_arry)):
                __point = 0.
                for j in range(len(word_arry[i])):
                    __out = 0.  # 出链数
                    if word_arry[i][j] != 0.:
                        for o in range(len(word_arry)):
                            __out += word_arry[o][j]
                        if __out != 0.:
                            __point += score[i] / __out
                score[i] = 1 - d + d * __point
                if abs(score[i] - score_back[j]) > max_diff:
                    max_diff = abs(score[i] - score_back[j])
        if max_diff < diff:
            return score
        return score

    def __create_word_map(self, sententce):
        word_map = {}
        index = 0
        for word in sententce:
            if word_map.has_key(word):
                continue
            word_map[word] = index
            index = index + 1
        return word_map

    @staticmethod
    def createList(row, line, value=0):
        if not (row > 0 and line > 0):
            raise Exception, 'row > 0 , line > 0'
        l = list()
        for i in range(row):
            l.append([])
            for j in range(line):
                l[i].append(value)
        return l



