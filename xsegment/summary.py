# coding=utf-8
#!/usr/bin/env python

import sys
from ZooSegment import FMM
from tag import HSpeech
from textrank import TextRank1
from b2 import system2
from b2 import object2
system2.reload_utf8()
"""自动摘要编写
    1. 基于权重式自动摘要实现； 基于句子权重，排序实现；
    2. 基于textrank摘要算法实现
"""





ITEM_LOCATION = object2.enum('BEGIN MEDIM END NONE')  # 位置变量


class WordItem(object):

    def __init__(self, word, tag, isKeyWord=False):
        self.word = word
        self.tag = tag
        self.isKeyWord = isKeyWord

    def __str__(self):
        msg = []
        for __key, __val in self.__dict__.items():
            if isinstance(__val, (list, tuple)):
                msg.append('%s %s' %
                           (__key, ' '.join([str(__v) for __v in __val])))
            else:
                msg.append('[%s %s]' % (__key, __val))
        return ' '.join(msg)


class Sentence(object):
    """句子信息存储结构体
        oristring 原始句内容
        index 原始句的位置
        loc 段落中的位置
        items 分词信息
        keywords 关键词数目
        score 关键句打分
        words 分词
        wordLen 句子含有的词数目　
    """
    def __init__(self, oristring, index, loc, words=None, items=None, keywords=None, wordLen=0, score=0.):
        self.index = index
        self.items = items
        self.score = score
        self.keywords = keywords
        self.oristring = oristring
        self.loc = loc
        self.words = words
        self.wordLen = wordLen

    def __str__(self):
        # 返回字符串功能　str()
        msg = []
        for __key, __val in self.__dict__.items():
            if isinstance(__val, (list, tuple)):
                msg.append('[ %s %s ]' %
                           (__key, ' '.join([str(__v) for __v in __val])))
            else:
                msg.append('[ %s %s ]' % (__key, __val))
        return '\n'.join(msg)


class Summary(object):
    """
    基于新闻的摘要功能　
    主要提取新闻关键句子　按照文章顺序输出
    """

    min_sentence_len = 8
    max_sentence_len = 25

    def __init__(self):
        raise NotImplementedError , 'no implement this func 【%s】' % sys._getframe().f_code.co_name

    def summary(self, content, title, summary_sentences=5, pagraph_split='\r\n'):
        """
        摘要主要接口
        content  新闻
        title 新闻的标题
        summary_sentences 返回的句子数目
        """
        # 是否要把标题作为句子切分　有待考虑
        sentences = self.split_sentence(title, pagraph_split)
        # 分割句子　－＞　将文本分割为　Sententce　ｌｉｓｔ
        sentences.extend(self.split_sentence(content, pagraph_split))
        self.segment(sentences)  # 分词　将所有句子对象转换为分词
        self.extractKeyWord(sentences, topN=30)  # 抽取关键词　
        self.score_sentences(sentences)  # 根据　句子信息对文章打分
        # 根据句子得分高低排序　得分高的在前面
        sentences = self.sentences_filter(sentences, 'score', reverse=True)
        summary_len = self.get_summary_len(len(sentences) ,  summary_sentences)

        # if len(sentences) > summary_sentences:  # 判断　是否超过需要的句子数目
        sentences = sentences[: summary_len]  # 句子数目
        sentences = self.sentences_filter(sentences, 'index')
        return (title, sentences)

    def get_summary_len(self,  sentences_length, summary_sentences):
        """
        设置摘要的大小
        如果为整数 ， 
            判断是否大于句子长度 ， 如果是返回设置的长度 ， 否则返回 判断是否大于句子长度
        如果为浮点数 ， 计算 句子数目 *取得比率 ， 判断计算的长度是否小于最小限制
        """
        if isinstance(summary_sentences, (float, int)):
            if summary_sentences > 1:
                return summary_sentences if summary_sentences <= sentences_length else sentences_length
            elif summary_sentences > 0:
                summary_calc_len = int(sentences_length * summary_sentences)
                if summary_calc_len < self.min_sentence_len:
                    if self.min_sentence_len > sentences_length:
                        return sentences_length
                    return self.min_sentence_len

                if summary_calc_len > self.max_sentence_len:
                    if self.max_sentence_len > sentences_length:
                        return sentences_length
                    return self.max_sentence_len
                return summary_calc_len
        raise TypeError, 'summary_sentences must be is int or folat '

    def split_sentence(self, content, split):
        """
        对输入的文本切分句子

        """
        if content:
            if isinstance(content, str):
                content = content.decode('utf-8')
            sentences = []
            index = 0
            for pagraph in content.split(split):  # 段落分隔符　是/r/n
                loc = ITEM_LOCATION.MEDIM
                split_last = 0
                save_sentences_len = len(sentences)
                pagraph = pagraph.strip()
                for i in range(len(pagraph)):
                    if pagraph[i] in ['!', '！', '?', '？', ';', '；']:
                        index = index + 1
                        sentences.append(
                            Sentence(pagraph[split_last: i + 1], index, loc))
                        split_last = i + 1
                    if pagraph[i] == '。':
                        if i > 1:
                            if pagraph[i - 1] in ['１', '２', '３', '４', '５', '６', '７', '８', '９', '０']:
                                if ((i + 1) < len(pagraph)) and pagraph[i + 1] in ['１', '２', '３', '４', '５', '６', '７', '８', '９', '０']:
                                    continue
                        index = index + 1
                        sentences.append(
                            Sentence(pagraph[split_last: i + 1].strip(), index, loc))
                        split_last = i + 1
                if split_last != len(pagraph):
                    sentences.append(
                        Sentence(pagraph[split_last:], index, ITEM_LOCATION.END))
                if len(sentences) > save_sentences_len:
                    sentences[save_sentences_len].loc = ITEM_LOCATION.BEGIN
                if len(sentences) > (save_sentences_len + 1):
                    sentences[-1].loc = ITEM_LOCATION.END
            return sentences
        return []

    def segment(self, sentences):
        """
        content : 每个要分词
        返回值：
        """
        raise NotImplementedError , 'no implement this func 【%s】' % sys._getframe().f_code.co_name

    def extractKeyWord(self, sentences, topN=20):
        """
        抽取关键词接口
        """
        raise NotImplementedError , 'no implement this func 【%s】' % sys._getframe().f_code.co_name

    def score_sentences(self, sentences):
        """
        每个句子单独打分
        """
        for i in range(len(sentences)):
            sentences[i].score = self.score(sentences[i])

    def score(self, sentence):
        """
        单句打分
        """
        raise NotImplementedError , 'no implement this func 【%s】' % sys._getframe().f_code.co_name

    def sentences_filter(self, sentences, order=None, reverse=False):
        """
        sentences : 每个文档的句子集合
        score : 阈值
        返回值: sentences
        """
        if sentences:
            if isinstance(sentences, list) and len(sentences) > 0:
                return sorted(sentences, key=lambda x: getattr(x, order), reverse=reverse)
        raise TypeError, 'sentences must be list and item is sententce'


class SimpleSummary(Summary):

    """
    默认自动摘要实现
    分词接口　: FMM  xsegment 或者含有接口为　segment　分词实现类别　　返回值为ｌｉｓｔ　或者　ｔｕｐｌｅ
    ｔａｇ　：　名词词性分析 现在直接调用　本人编写的词性标注类实现
    """

    def __init__(self, segment=None, tag=None):
        if segment:
            self.__segment = segment
        else:
            self.__segment = FMM()
        if tag:
            self.__tag = tag
        else:
            self.__tag = HSpeech()

    def segment(self, sentences):
        for i in range(len(sentences)):
            sentences[i].words = self.__segment.segment(sentences[i].oristring)
            sentences[i].wordLen = len(sentences[i].words)
            items = []
            tags = self.__tag.tag(sentences[i].words)
            if tags:
                sentences[i].items = [WordItem(__word[0], __word[1])
                                      for __word in tags]
            else:
                sentences[i].items = []

    def extractKeyWord(self, sentences, topN=20):
        words = []
        for i in range(len(sentences)):
            words.extend(
                [item.word for item in sentences[i].items
                 if len(item.tag) > 0
                 and item.tag[0] in ['n', 'r', 'v']
                 and len(item.word) > 1 and i > 0]
            )
        keywords = TextRank1.extract_key_word(words, 3, topN)
        keywords.extend(
            [item.word for item in sentences[1].items if len(item.tag) > 0 and item.tag[0] in ['n', 'r', 'v']])
        for i in range(len(sentences)):
            keyWordsLen = 0
            for j in range(len(sentences[i].items)):
                if sentences[i].items[j].word in keywords:
                    sentences[i].items[j].isKeyWord = True
                    keyWordsLen = keyWordsLen + 1
            sentences[i].keywords = keyWordsLen

    def score(self, sentence):
        if sentence.wordLen <= 0:
            return -30
        __score = 0.
        if sentence.loc == ITEM_LOCATION.BEGIN:
            __score += 10
        if sentence.loc == ITEM_LOCATION.END:
            __score += 6
        __score = sentence.keywords * 80.0 / sentence.wordLen
        if sentence.oristring.strip()[-1] in ['?', '!', '？', '!']:
            __score -= 100
        if len(sentence.oristring.strip()) < 5:
            __score -= 10
        return __score

    def __cos(self, sentence1, sentence2, split_word=' '):
        if sentence1 and sentence2:
            if isinstance(sentence1, (str, unicode)) and isinstance(sentence2, (str, unicode)):
                sentence1 = [word for word in sentence1.split(split_word)]
                sentence2 = [word for word in sentence2.split(split_word)]
            elif isinstance(sentence1, (list, tuple)) and isinstance(sentence2, (list, tuple)):
                raise NotImplementedError , 'no implement this func 【%s】' % sys._getframe().f_code.co_name
            else:
                raise TypeError



class WeightArray(object):

    def __init__(self, sentences , distance_fun):
        self.sentences = sentences 
        self.distance_map = self.create_distance_map(sentences, distance_fun)
        self.data_len = len(sentences)




    def __getitem__(self, label_tuple):
        row , line = label_tuple        
        return self.get_distance_by_index(row , line)



    def get_distance_by_index(self  , row , line ):
        """得到权重矩阵的value值
            param:row:权重矩阵的横坐标
            param:line:权重矩阵的纵坐标
            rerurn:value:如果有权重值的话，反悔权重值
            raise:IndexError:
        """
        if line > row :
            tmp = row 
            row = line 
            line = tmp  
        return self.distance_map[row][line]



    def create_distance_map(self, sentences, distance_fun):
        """创建数据距离map
        params:sentences:数据，格式 [[label1 , x1 ,x2...,xN ] , [lable2 , x1 , x2 , ..., xN]....[labelN , x1, x2 , ...xN] ]
        return:sentence_map
        """
        distance_map = []
        for i in range(len(sentences)):
            tmp_distance = []
            for j in range(i + 1):
                if i == j:
                    tmp_distance.append(0)
                else:
                    tmp_distance.append(distance_fun(sentences[i], sentences[j]))
            distance_map.append(tmp_distance)
        return distance_map

import math 
from collections import Counter

class TextRankSummary(Summary):

    """docstring for TextRankSummary"""

    def __init__(self , d = 0.85 , threshold = 0.05 ,iter_count = 100 ):
        super(TextRankSummary, self).__init__()

        self.d = d #阻尼系数
        self.iter_count = iter_count #迭代次数
        self.threshold = threshold #阈值 ， 设置此值后 ， 在计算rank的时候，如果小于这个数值时，跳出迭代

    def summary(self, content, title, summary_sentences=5, pagraph_split='\r\n'):
        sentences = self.split_sentence(content ,split = pagraph_split )
        self.segment(sentences)
        sentence_weight_map = WeightArray(sentences , self.distance)
        sentence_score_order = self.rank(self.iter_count , 0.01 , sentence_weight_map , len(sentences) , self.d )
        summary_len = self.get_summary_len(len(sentences) ,  summary_sentences)
        return '\n'.join([sentences[sentence_score_order[i][1]].oristring for i in range(summary_len)])

    def rank(self , iter_count  , threshold ,sentence_weight_map , sentence_len , d = 0.8  ):
        """
        功能:
            param1 
                sentence_distance_map 句子相似度矩阵
                sentence_len 句子总数
            return 
                sentences_score  句子权重值打分
        """
        
        #初始化句子权重 ，暂时定位1 
        sentences_score = [ 1 - d   for i in  range(sentence_len)]
        sentence_out_sum = [] # 每个句子出链的权重比值
        for i in range(sentence_len):
            sentence_out_sum.append( sum(sentence_weight_map[(i , j)] for j in range(sentence_len)))

        #weight_sum 
        for _ in range(iter_count):
            tmp_score = copy(sentences_score)
            max_diff = None 
            for i in range(sentence_len):
                #所有句子都是入链
                for j in range(sentence_len):
                    if i == j:
                        continue
                    tmp_score[i] +=  d * sentence_weight_map[(i , j )] / sentence_out_sum[j] * sentences_score[j] 
                diff = abs( tmp_score[i] - sentences_score[i] )
                if max_diff == None or diff > max_diff:
                    max_diff = diff 
            sentences_score = tmp_score
            if max_diff  < threshold:
                break 
        return sorted([(sentences_score[i] , i )  for i in range(sentence_len) ] , key =lambda x :  float(x[0]) ,reverse = False) 

    def segment(self, sentences):
        for sentence in sentences:
            sentence.words = [ sentence.oristring[i : i + 2] for i in range( len(sentence.oristring) - 2)]
            sentence.words_len = len(sentence.words)


    def distance(self , sentence1 , sentence2 ):
        vector1 = Counter(sentence1.words)
        vector2 = Counter(sentence2.words)
        words_bag = set(vector2.keys()) & set(vector2.keys())
        up = sum([vector1[x] * vector2[x] for x in words_bag])
        down  = math.sqrt(sum([ vector1[word] ** 2 for word in vector1.keys()] ) ) * \
            math.sqrt(sum([vector2[word] ** 2 for word in vector2.keys()]))
        return float(up) / down 


if __name__ == '__main__':

    s = SimpleSummary()
    x = None
    with open('d:/feiji') as f:
        x = ''.join([line for line in f.readlines() if line.strip() != ''])
    with open('d:/summary.txt' , 'w') as f:
        for i in s.summary(x, '康佳携手万合天宜启动新生代历练计划', summary_sentences=0.08)[1]:
            f.write(i.oristring + "\n")
