# coding=utf-8
#!/usr/bin/env python


from collections import defaultdict
from ctypes import c_uint64


class SimHash(object):

    '''
    simhash 海明距离计算
    词——》 hash
    数字权重计算
    逐位计算
    取反取距离
    '''

    __seg = None  # 分词藉口
    word_hash_dict = defaultdict()  # word——hash 保存

    def __init__(self, segfun=None):
        self.__seg = segfun

    def figureprint(self, document):
        '''
        计算海明编码
        '''
        if document and isinstance(document, (str, unicode)):
            words = self.__seg(document)
            wm = defaultdict(int)  # 词hash->出现次数
            for word in words:  # 循环分词
                if word not in self.word_hash_dict:
                    self.word_hash_dict[word] = self.hash(word)
                wm[self.word_hash_dict[word]] += 1
            hash_array = [0 for i in range(64)]  # 所有ｈａｓｈ值相加减数组
            for hash_num, weight in wm.items():  # 循环数组　权重
                hash_array = self.hash_array_add(
                    hash_array, self.to_array(hash_num, weight))
            return self.array_to_int(hash_array)  # 转换为数字
        raise ValueError , "document is string !"

    def array_to_int(self, hash_array):
        if isinstance(hash_array, (tuple, list)):
            return sum(1 << i for i in range(len(hash_array)) if hash_array[i] > 0)
        raise TypeError, "hash_array type is list or tuple "

    def hash_array_add(self, hash_array1, hash_array2):
        if len(hash_array1) == len(hash_array2) == 64:
            return [hash_array1[i] + hash_array2[i] for i in range(64)]
        raise ValueError

    def to_array(self, hash_num, weight):
        return [-weight if (hash_num >> i) == 0 else weight for i in range(64)]

    def hash(self, word):
        '''
        对字符串ｈａｓｈ作用

        '''
        return hash(word) & 0xFFFFFFFF 

    @staticmethod
    def distance(sh1, sh2):
        if not (isinstance(sh1, (int , long )) and isinstance(sh2, (int,long))):
            raise TypeError, '参数必须为整数 !'
        h = (sh1 ^ sh2) & (1 << 64 - 1)
        d = 0
        while h:
            h = h & (h - 1)
            d += 1
        return d


if __name__ == '__main__':
    f = SimHash(lambda x: x.split())
    print f.figureprint('hello')
    print f.figureprint('i have a box !') ^ f.figureprint('i have a cat !')
    print f.figureprint('he have cat')
    print f.figureprint('i have a cat !')
    print SimHash.distance(f.figureprint('he have cat !'), f.figureprint('i have a cat !'))
    print f.hash('a')
