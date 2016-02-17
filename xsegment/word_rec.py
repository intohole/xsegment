#coding=utf-8

"""利用管道实现 <<互联网时代的社会语言学：基于SNS的文本数据挖掘>>
    http://www.matrix67.com/blog/archives/5044
"""
import os
import re
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import collections
import json
import math

def entropy( probs ):
    if isinstance(probs , (list , tuple)) is False or len(probs) == 0:
        return None
    return sum([ -prob * math.log(prob,2) for prob in probs])


class WordRecPrepare(object):


    def __init__(self , word_dict_path):
        self.word_freq = collections.defaultdict(int)
        self.save_path = word_dict_path



    def add(self , line):
        words = line.split()
        for word in words:
            word = word.decode("utf-8")
            if len(word) < 2:
                continue 
            self.word_freq[word[-1]] += 1
            for i in range(len(word)-1):
                cur_word = word[i : i + 2]
                self.word_freq[word[i]] += 1
                print "%s\t%s\t%s" % ( cur_word , "word" , 1)
                if i != 0: 
                    # 左邻字
                    print "%s\t%s\t%s" % (cur_word , "left" ,word[i-1])
                if i < (len(word) -2):
                    # 右邻字
                    print "%s\t%s\t%s" % (cur_word , "right" ,word[i + 2])

    def save_dict(self):
        """保存字的出现频率词典
            params:
            return:
            raise:
        """
        with open(save_path , "w") as f:
            f.write("sum\t%s\n"  % sum(word_freq.values()))
            for word,count in word_freq.items():
                f.write("%s\t%s\n" % (word , count)) 

class WordRec(object):



    def __init__(self , word_dict_path  ,word_limit , left_entropy_limit , right_entropy_limit):
        self.save_path = word_dict_path
        word_sum , word_freq_dict = self.loads(self.save_path)
        self.word_sum = word_sum 
        self.word_freq_dict = word_freq_dict 
        self.word_limit = word_limit 
        self.left_entropy_limit = left_entropy_limit
        self.right_entropy_limit = right_entropy_limit
    
    def loads(self):
        word_freq = collections.defaultdict(int)
        with open(dict_path) as f:
            word_sum = float(f.readline().rstrip().split("\t")[1]) 
            for line in f.readlines():
                word , freq = line.rstrip().split("\t")
                word_freq[word.decode("utf-8")] = int(freq)
        return word_sum , word_freq
    

    def extract(self):
        last_word = ""
        word_count = 0
        left_entropy_dict = collections.defaultdict(float)
        right_entropy_dict = collections.defaultdict(float)
        for line in sys.stdin:
            word , sign , value = line.rstrip().split("\t") 
            word = word.decode("utf-8")
            if last_word != word:
                if last_word != "":
                    word_rate = word_count / self.word_sum 
                    word_limit = (self.word_freq_dict[word[0]] /self.word_sum * selfword_freq[word[1]]/word_sum)  
                    if word_limit > self.word_limit:
                        left_entropy = 1 
                        if len(word_left) >0:
                            left_sum = float(sum(word_left.values()))
                            left_entropy =  entropy([ l/left_sum  for l in word_left.values()])
                        right_entropy = 1 
                        if len(word_right) >0:
                            right_sum = float(sum(word_left.values()))
                            right_entropy =  entropy([ l/left_sum  for l in word_right.values()])
                            
                        if left_entropy > left_entropy_limit and right_entropy > right_entropy_limit: 
                            print last_word,left_entropy,right_entropy 
                last_word = word 
                word_count = 0
                word_left.clear()
                word_right.clear()
            if sign == "word":
                word_count += 1
            elif sign == "left":
                value = value.decode("utf-8")
                word_left[value] += 1
            elif sign == "right":
                value = value.decode("utf-8")
                word_right[value] += 1
    
if __name__ == "__main__":
    if sys.argv[1] == "wordsplit":
        word_split(sys.argv[2])
    elif sys.argv[1] == "wordrec":
       word_rec(sys.argv[2] , float(sys.argv[3]) , float(sys.argv[4]) , float(sys.argv[5])) 
