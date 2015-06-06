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


class TextRank1(object):

    """"""

    '''
    功能列表：
    create_word_window(sentence , window_size , weight)
    sentence:
            分析的文档分词 ， 分词结果 ， 分词结果任意分隔符空格 、 tab键 或者类型为list的分词结果 
    window_size ：
             关键词前后入链的窗口大小 
    weight：
           计算窗口的时候是否加入权重
    return {词 : 入链词的set}

    '''

    @staticmethod
    def create_word_window(sentence, window_size, weight=False):
        '''
        方法： 创建一个词窗口 格式 ： 词 -》 窗口词
              返回值：
        '''
        if sentence and len(sentence) > 0:
            if isinstance(sentence, (str, unicode)):
                sentence = split(sentence)
            elif not isinstance(sentence, (list, tuple)):
                raise Exception, '%s is type erro!' % sentence
            if not weight:
                word_window = defaultdict(set)
            else:
                word_window = defaultdict(list)
            # 这里没有处理 ， 窗口与字符串长度判断
            sentence_new = [
                word for word in sentence if chinese(word.decode('utf-8'))]
            for i in range(window_size, len(sentence_new)):
                for j in range(i - window_size, i):
                    if not weight:
                        word_window[sentence_new[i]].add(sentence_new[j])
                    else:
                        word_window[sentence_new[i]].append(sentence_new[j])
            return word_window
        return None

    @staticmethod
    def textrank(word_window, iter_count=20, diff=0.000001, d=0.85):
        '''
        textrank 参照论文 ： TextRank: Bringing Order into Texts
        原理 ： 根据词窗口 建立边 词 ： 顶点
        迭代公式 ： score(Vi) = 1- d * sum(In(Vi)) * 1/ out(Vj) * score(Vj)
        Vi ，Vj 就是任意点
        参数 ： word_window  是 词- 》 该词前面n个窗口的词（）
               iter_count 迭代次数
               diff 两次迭代最小变化值
               d 阻尼系数

        '''
        if isinstance(word_window, dict):
            scoreDict = defaultdict(float)
            tmp = defaultdict(dict)
            for __key in word_window.keys():
                scoreDict[__key] = 1.
            for _ in range(iter_count):
                max_diff = 0. 
                cur_score_map = scoreDict.copy() # 保存上次计算每个词的分数值 ， 为了后面确定是否跳出循环 ， 两次差小于一定值
                for __key, __val in word_window.items():
                    score = 0.
                    for __word in __val:  # 循环每个窗口词
                        __out = 0  # 出链数目
                        if word_window.has_key(__word):
                            __out = len(word_window[__word])  # 每个词的出链 ， 窗口
                        if __word == __key or __out == 0:
                            continue
                        score += cur_score_map[__word] / __out
                    cur_score_map[__key] = 1 - d + d * score
                    __diff = abs(cur_score_map[__key] - scoreDict[__key])
                    if max_diff < __diff:
                        max_diff = __diff
                for __key in scoreDict.keys():
                    scoreDict[__key] = cur_score_map[__key]
                if max_diff <= diff:
                    break
            return scoreDict

    @staticmethod
    def sort_score(scoreDict, topN=None):
        size = len(scoreDict)
        if size == 0: #如果没有任何词 ， 则返回一个空list
            return []
        if isinstance(topN , int):
            topN = min(size , topN)
        elif isinstance(topN , float):
            topN = min(topN * size , size)
        else:
            raise TypeError , 'topN input Type is erro must be float or int or value is None , size type\'s %s' % type(topN)
        keywords = [(__key, __val) for __key, __val in scoreDict.items()]
        keywords = sorted(keywords, key=lambda x: x[1], reverse=True)
        return keywords[:topN]

    @staticmethod
    def extract_key_word(words, window_size, topN=None,  weight=False, iter_count=20, diff=0.000001, d=0.85):
        '''
        words
           提取关键的文档 ， 文档格式必须是空格、tab键分割的字符串 或者 分词结果保存的list ，tuple
        window_size:
           创建一个词窗口 ， 表示词窗口的大小 
        topN:
            默认值 False
            参数说明：
                取得top关键词 
                topN == None 返回全量排序的关键词 【降序排列】
                topN 是整数返回min(词数，topN)关键词
                topN 是浮点数 ， 则返回词数*topN 与词数最小值
                如果不满足以上情况：
                    抛出异常 ， 类型检查失败
        weight :
            默认值： False
            是否使用权重计算
        iter_count:
            默认值： 20
            textrank 迭代次数
        diff :
             默认值 ： 0.000001
             textrank 如果两轮迭代满足差 ，小于等于此值 ， 跳出迭代
        d:
             阻尼系数 ， 模拟任何跳出任何跳出窗口的概率

        '''
        word_windows =TextRank1.create_word_window(words, window_size, weight)
        keywords_map = TextRank1.textrank(word_windows, iter_count, diff, d)
        return TextRank1.sort_score(keywords_map, topN)


