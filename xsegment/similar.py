# coding=utf-8




import math
from collections import defaultdict
from collections import Counter
from ctypes import c_uint64
import sys
import os
from tfidf import TfIdf 
from b2.ds2 import DTrie

__all__ = ["consine","SimHash",""]



def _consine(vector1,vector2):
    """calc vector consine distance
    """
    if vector1 is None or vector2 is None:
        raise ValueError
    if len(vector1) != len(vector2):
        raise IndexError("")
    return math.sqrt(sum(v1 * v2 for v1,v2 in zip(vector1,vector2))) /\
            math.sqrt(sum(v1**2 for v1 in vector1)) * math.sqrt(sum(v2 ** 2 for v2 in vector2))

def _consineDict(vector1,vector2):
    if vector1 is None or vector2 is None:
        raise ValueError
    vectorBag = set(vector1.keys()) & set(vector2.keys())
    return _consine(
                [float(vector1[key]) if key in vector1 else 0. for key in vectorBag],
                [float(vector2[key]) if key in vector2 else 0. for key in vectorBag],
            )
    

def consine(sentence1, sentence2, split_function=lambda x: x.split()):
    """consine calc doc similarty
    """
    vector1 = Counter(split_function(sentence1))
    vector2 = Counter(split_function(sentence2))
    return _consineDict(vector1,vector2)

class SimHash(object):
    """文档的simhash算法实现，用于文档粗略相似度计算实现
        Test:
            >>> def segfun(words):
            ...     return [ words[i:i+2] for i in range(len(words) - 1)]
            >>> s = SimHash( segfun = segfun)
            >>> s.figureprint("abc") == s.figureprint("abc")
            >>> s.figureprint("abc") == s.figureprint("abcd")
            >>> s.distance(s.figureprint("abc") , s.figureprint("abcde"))
    """


    def __init__(self, segfun=None , base = 64 ):
        """初始化simhash计算方法
            :param:segfun:callable:split words function , like this lambda x: x.split()
            :param:base:int:
       """
        if segfun is None or not callable(segfun):
            raise ValueError, 'segfun is function which to split sentence or document to items function'
        if base is None or isinstance(base , int) is False or base % 32 != 0 and base <= 0:
            raise ValueError
        self.seg = segfun 
        self.base_range = xrange(base)
        self.base = base
        self.word_hash_dict = defaultdict()  # word——hash 保存
        self.seg = segfun
        self.LONG_MAX = ((1 << base)  - 1)

    def create_array(self, default_value=0.):
        """create array with init by default value
        
        :param default_value: default value 
        :param list:array 
       """
        return [ default_value for i in self.base_range ]

    def figureprint(self, document):
        """calc figureprint of document 
            params:
                document                需要计算sim_hash数值的字符串
            return 
                value                   文档的simhash数值
            raise 
                None
        """
        if document and isinstance(document, (str, unicode)):
            words = self.seg(document)
            hash_count_dict = Counter([self.hash(word) for word in words])
            hash_array = self.create_array()
            for hash_num, weight in hash_count_dict.items():  # 循环数组　权重
                self._hash_array_add(
                    hash_array, self.get_array_by_weight(hash_num, weight))
            return self._array_to_int(hash_array)  # 转换为数字
        raise ValueError, "document is string !"

    def _array_to_int(self, hash_array):
        """将hash数组转换成为整型
            主要思想为hash_array大于0该位为1，否则为0
            params:
                hash_array              hash数组
            return 
                value                   hash数组转换成为的整型
            raise
                TypeError               hash_array类型不为数组的时候
        """
        if hash_array and isinstance(hash_array, (tuple, list)):
            return sum(1 << i for i in self.base_range if hash_array[i] > 0) & self.LONG_MAX
        raise TypeError, "hash_array type is list or tuple "

    def _hash_array_add(self, hash_array1, hash_array2):
        """将第二个hash数组累加到第一个数组中
            params:
                hash_array1             hash数组1
                hash_array2             hash数组2 
            return 
                hash_array1             将hash_array2数组累加到hash_array1上返回o
            raise 
                ValueError              两个数组长度不相等或者不与要求数组长度一致抛出异常
        """
        if len(hash_array1) == len(hash_array2) == self.base:
            for i in self.base_range:
                hash_array1[i] += hash_array2[i]
            return
        raise ValueError

    def get_array_by_weight(self, hash_num, weight):
        return [-weight if (hash_num & (1 << i)) == 0 else weight for i in range(64)]
    
    def hash(self, word):
        """对word单次hash操作
            params:
                word                计算hash值的字符串
            return 
                long                字符串的hash值
            raise:
                None
        """
        return hash(word) & self.LONG_MAX

    def distance(self , sh1, sh2 ):
        """计算两个字符串的相似程度
            params
                sh1                 字符串simhash数值
                sh2                 字符串simhash数值
            return 
                value               返回sh1与sh2距离
            raise 
                TypeError
        """
        if not (isinstance(sh1, (int, long)) and isinstance(sh2, (int, long))):
            raise TypeError, '参数必须为整数 !'
        h = (sh1 ^ sh2) & self.LONG_MAX
        d = 0
        while h:
            h = h & (h - 1)
            d += 1
        return d




class Vsm(object):


    def __init__(self,idffile = None):
        self.tfidf = TfIdf(idffile)
        self._calc = False 

    def addDoc(self,doc):
        self.tfidf.add(doc) 
        self._calc = False

    def similarty(self, doc1, doc2):
        if self._calc is False:
            self.tfidf.train()
        vector1 = self.tfidf.calc(doc1,r="dict",sort=False)
        vector2 = self.tfidf.calc(doc2,r="dict",sort=False)
        return _consineDict(vector1,vector2) 



class CiLin(DTrie):

    def to_element(self, element):
        elements = []
        word_len = len(element)
        if word_len >= 1:
            elements.append(element[0])
        if word_len >= 2:
            elements.append(element[1])
        if word_len >= 4:
            elements.append(element[2:4])
        if word_len >=5:
            elements.append(element[4])
        if word_len >=7:
            elements.append(element[5:7])
        return elements


class WordSim(object):

    def __init__(self, dictpath=os.path.join(os.path.abspath(os.path.dirname(__file__)),  'dict/cilin.txt'), a=0.65, b=0.8, c=0.9, d=0.96 ,e=0.5, f=0.1):
        self.wordForest = CiLin()
        self.word_dict = defaultdict(list)
        self.load_dict(dictpath)
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f

    def load_dict(self, dictpath):
        with open(dictpath) as f:
            for line in f.readlines():
                line = line.strip().split('=')
                if len(line) == 2:
                    self.wordForest.add(line[0])
                    for word in line[1].split():
                        if word != "":
                            self.word_dict[word].append(line[0])

    def word_sim(self, word1, word2 , desc = True):
        '''
        计算两个词的相似度 [0 , 1]
        word1 : 计算词1
        word2 : 计算词2
        desc : 是否降序排列 ， 默认降序排列
        exception : 
            如果word1 不是字符串或者为空 ， 抛出 ValueError
            如果word2 不是字符串或者为空 ， 抛出 ValueError
        返回：
            相似度list
        '''
        word1_vector = self.get_word_vector(word1)
        if word1_vector == None:
            return None
            # raise ValueError, '%s not included in dict !' % word1
        word2_vector = self.get_word_vector(word2)
        if word2_vector == None:
            return None 
            # raise ValueError, '%s not included in dict !' % word2
        result = []
        for v1 in word1_vector:
            for v2 in word2_vector:
                result.append(self.__calc_sim(v1 , v2))
        return sorted(result  , reverse = desc)
    
    def __calc_sim(self , vector1 , vector2):
        head_path = self.__get_same_start(vector1 , vector2)
        if  len(head_path) == 0:
            return self.f
        n = self.wordForest.getChildNum(head_path)
        if len(head_path) == 1:
            k = abs( ord(vector1[1]) - ord(vector2[1]))
            return self.__sim(self.a , n , k)
        elif len(head_path) == 2 :
            k = abs( int(vector1[2:4]) - int(vector2[2:4]))
            return self.__sim(self.b , n , k)
        elif len(head_path) == 4:
            k = abs( ord(vector1[4]) -  ord(vector2[4]))
            return self.__sim(self.c , n , k)
        elif len(head_path) == 5:
            k = abs( int(vector1[5:7]) -  int(vector2[5:7]))
            return self.__sim(self.d , n , k)
        elif len(head_path) >=6:
            if vector1[-1] == '=':
                return 1.
            elif vector1[-1] == '#':
                return self.e
            else:
                return 1.

    def __sim(self , var , child_num , length):
        return var * math.cos( child_num * math.pi /  180  ) * ( float(child_num -length + 1 ) / child_num )


    def get_word_vector(self, word):
        if not (word and isinstance(word, (str, unicode))):
            raise ValueError, 'word not string or emtpy!'
        if self.word_dict.has_key(word):
            return self.word_dict[word]
        else:
            return None

    def __get_same_start(self , word1 , word2):
        word_len = min(len(word1) , len(word2))
        for i in range(word_len):
            if word1[i] != word2[i]:
                return word1[:i]
        return word1[:word_len]



if __name__ == '__main__':

    v = Vsm()
    v.addDoc('a b c d c a')
    v.addDoc('a b c d c a')
    v.addDoc('c d f e r a c')
    # print v.totfidf()
    print v.similarty('a c d', 'b c')
