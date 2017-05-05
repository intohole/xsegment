#coding=utf-8


from collections import defaultdict
from collections import Counter
import json
import math
import os


__all__ = ["TfIdf"]

class TfIdf(object):
    """关键词提取工具
    """


    def __init__(self,idf_file):
        """初始化tfidf计算工具
            param:tfidf_file:basestring:保存idf数据文件，文件为json存储
        """
        self.doc_count = 0
        self.word_doc_info = defaultdict(int)
        self.default_idf = None
        self.tfidf_file = tfidf_file
        self.idf = defaultdict(float) or self.load()
        

    def add(self,doc):
        """添加文档函数
            param:doc:(bastring|list|tuple):添加的文档字段，如果为字符串，使用空格分割；或是用list，tuple来存储
            raise:TypeError:如果doc类型不在(basestring,list,tuple)，抛出异常
        """
        if isinstance(doc,basestring):
            doc = doc.split()
        elif isinstance(doc,(list,tuple)):
            pass
        else:
            raise TypeError("Unsupported type {}".format(type(doc).__name__))
        for item in doc:
            self.word_doc_info[item] += 1
        self.doc_count += 1

    def train(self):
        """进行idf统计函数
        """
        for item,count in self.word_doc_info:
            self.idf[item] = math.log(self.doc_count / (count + 1.),2)  
    
    def get_idf(self, word):
        if word in self.idf:
            return self.idf[word]
        if self.default_idf is None:
            self.default_idf = math.log(self.doc_count / 1. ,2 )
        return self.default_idf

    def load(self):
        if not os.path.exists(self.tfidf_file) or not os.path.isfile(self.tfidf_file):
            return None
            
        
        with open(self.tfidf_file) as f:
            return json.loads(f.readline())  
    
    def save(self):
        with open(self.tfidf_file,"w") as f:
            f.write(json.dumps(self.idf) + "\n")

    def calc(self,doc,sort = True):
        """计算文档内部所有词的tfidf
            param:doc:(bastring|list|tuple):需要计算文档集合
            param:sort:Boolean:是否需要排序返回，如果为True，整体按照tfidf排序
            return:array:list[(word,tfidf)]:文档tfidf数组
        """
        if doc is None:
            raise ValueError("doc is none!") 
        if isinstance(doc,basestring):
            doc = doc.split()
        elif isinstance(doc,(list,tuple)):
            pass
        else:
            raise TypeError("Unsupported type {}".format(type(doc).__name__))
        wordCounter = Counter(doc) 
        word_array = [ (word,tf * self.get_idf(word) ) for word,tf in wordCounter.items()] 
        return sorted(word_array,lambda x:x[1],reverse = False) if sort is True else word_array
