# coding=utf-8
#!/usr/bin/env python


from collections import defaultdict
from collections import Counter
from ctypes import c_uint64
import sys


__all__ = ["SimHash"]

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
            params:
                segfun                  分词函数
                base                    整形位数
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
        """创建一个变量数组，存储字符串hash数值
            params:
                default_value           默认值
            return 
                []                      hash值转换成为数组的数值
            raise 
                None 
        """
        return [ default_value for i in self.base_range ]

    def figureprint(self, document):
        """计算文档simhash数值，文档指纹
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
