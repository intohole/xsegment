# coding=utf-8
#!/usr/bin/env python


from collections import defaultdict
from ctypes import c_uint64


class SimHash(object):

    '''simhash 海明距离计算
        计算字符串直接距离算法，主要用于文档直接粗相似度计算；
    '''

    seg = None  # 分词接口
    word_hash_dict = defaultdict()  # word——hash 保存
    LONG_MAX = (1 << 64 - 1)

    def __init__(self, segfun=None):
        if segfun is None or not callable(segfun):
            raise ValueError, 'segfun is function which to split sentence or document to items function'
        self.seg = segfun

    def get_array_by_size(self, size, default_value=0):
        return [0 for i in range(size)]

    def figureprint(self, document):
        '''计算文档simhash值
        '''
        if document and isinstance(document, (str, unicode)):
            words = self.seg(document)
            hash_count_dict = defaultdict(int)  # 词hash->出现次数
            for word in words:  # 循环分词
                if word not in self.word_hash_dict:
                    self.word_hash_dict[word] = self.hash(word)
                hash_count_dict[self.word_hash_dict[word]] += 1
            hash_array = self.get_array_by_size(64)
            for hash_num, weight in hash_count_dict.items():  # 循环数组　权重
                self.hash_array_add(
                    hash_array, self.get_array_by_weight(hash_num, weight))
            return self.array_to_int(hash_array)  # 转换为数字
        raise ValueError, "document is string !"

    def array_to_int(self, hash_array):
        if isinstance(hash_array, (tuple, list)):
            return sum(1 << i for i in range(len(hash_array)) if hash_array[i] > 0)
        raise TypeError, "hash_array type is list or tuple "

    def hash_array_add(self, hash_array1, hash_array2):
        if len(hash_array1) == len(hash_array2) == 64:
            for i in range(64):
                hash_array1[i] += hash_array2[i]
            return
        raise ValueError

    def get_array_by_weight(self, hash_num, weight):
        return [-weight if (hash_num & (1 << i)) == 0 else weight for i in range(64)]

    def hash(self, word):
        '''对字符串ｈａｓｈ作用
        '''
        return hash(word) & self.LONG_MAX

    def distance(sh1, sh2):
        if not (isinstance(sh1, (int, long)) and isinstance(sh2, (int, long))):
            raise TypeError, '参数必须为整数 !'
        h = (sh1 ^ sh2) & self.LONG_MAX
        d = 0
        while h:
            h = h & (h - 1)
            d += 1
        return d
