#coding=utf-8



from xsegment.wordsim import WordTrie
from xsegment.wordsim import WordSim

if __name__ == '__main__':
    w = WordTrie()
    w.add('abc')
    w.add('adc')
    print w.get_child_num('a')
    w = WordSim()
    print w.word_sim('人民供' , '国民')
    print w.word_sim('人民' , '群众')
    print w.word_sim('人民' , '先锋')
    print w.word_sim('骄傲' , '谦虚')
