#coding=utf-8

from moodstyle.alg.PageRank import PageRank
from moodstyle.alg.PageRank import GraphV2
from moodstyle.text.Ngram import ngram2List
from b2 import exceptions2
from b2 import object2
from b2 import sort2
from itertools import combinations


class TextRank(object):
    """ TextRank implemention
    """

    @staticmethod
    def extract_key_word(words,
                         window_size,
                         topN=None,
                         weight=False,
                         iter_count=20,
                         diff=0.000001,
                         d=0.85):
        """
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
        Test:
            >>> TextRank.extract_key_word("a b c d a c d a c b",3)
            [('c', 0.26925141607071224), ('d', 0.26447844103609264), ('a', 0.22016262103687753), ('b', 0.2060871096788397)]
            >>> TextRank.extract_key_word("a b c d a c d a c b",3,topN = 2)
            [('c', 0.26925141607071224), ('d', 0.26447844103609264)]
            >>> TextRank.extract_key_word("a b c d a c d a c b",4)
            [('a', 0.23160677474223332), ('c', 0.23160674736544368), ('d', 0.23160674195403314), ('b', 0.19795448492772966)]
        """
        wordId = object2.AutoID()
        word_windows = ngram2List(words, n=window_size)
        for words in word_windows:
            wordId.extend(words)
        graph = GraphV2(len(wordId))
        for words in word_windows:
            for x, y in combinations(words, 2):
                graph.add_edge(wordId[x], wordId[y])
        rank = PageRank()
        weights = rank.rank(graph, iter_count=iter_count, d=d, min_error=diff)
        wordsWeightDict = {
            wordId.get_by_id(index): weight
            for index, weight in enumerate(weights)
        }
        topN = len(weights) if topN is None else topN * len(
            weights) if isinstance(topN, float) else topN
        return sort2.sort_map_value(wordsWeightDict, desc=True)[:topN]


if __name__ == "__main__":
    print TextRank.extract_key_word("a b c d d a c a b", 3)
