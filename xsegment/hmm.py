# coding=utf-8
#!/usr/bin/env python

from collections import defaultdict
import sys
import os
import json
reload(sys)
sys.setdefaultencoding('utf-8')
import re





class HSegment(object):
    __start_state = None
    __emission_probability = None
    __transition_probability = None
    __states = ['s', 'm', 'b', 'e']
    __split = re.compile('\\s+').split

    def __init__(self, model=os.path.join(os.path.abspath(os.path.dirname(__file__)),  'dict')):
        self.__load(model)

    def __load(self, path):
        if path:
            if not path.endswith('/'):
                path = path + '/'
        with open('%s%s' % (path, 'start_state.txt')) as f:
            self.__start_state = json.loads(f.readline())
        # print self.__start_state
        with open('%s%s' % (path, 'emission_probability.txt')) as f:
            self.__emission_probability = json.loads(f.readline())
        # print self.__emission_probability
        with open('%s%s' % (path, 'transition_probability.txt')) as f:
            self.__transition_probability = json.loads(f.readline())
        # print self.__transition_probability

    def __viterbi(self, obs):
        '''
        特比算法 摘自wiki 维特比算法
        '''
        # print obs
        V = [{}]
        path = {}
        for y in self.__states:
            V[0][y] = self.__start_state[y] * \
                self.__emission_probability[y][obs[0]]
            path[y] = [y]
        for t in range(1, len(obs)):
            V.append({})
            newpath = {}
            for y in self.__states:
                (prob, state) = max(
                    [(V[t - 1][y0] * self.__transition_probability[y0][y] * self.__emission_probability[y][obs[t]], y0) for y0 in self.__states])
                V[t][y] = prob
                newpath[y] = path[state] + [y]
            path = newpath
        (prob, state) = max([(V[len(obs) - 1][y], y) for y in self.__states])
        return (prob, path[state])

    def __segment(self, sentence):
        if sentence and isinstance(sentence , basestring) and len(sentence.strip()):
            if not isinstance(sentence , unicode):
                sentence = sentence.decode('utf-8')
            obstates = self.__viterbi(sentence)[1]
            word = []
            for i in range(len(obstates)):
                if obstates[i] == 's':
                    yield sentence[i]
                elif obstates[i] == 'b':
                    del word[:]
                    word.append(sentence[i])
                elif obstates[i] == 'm':
                    word.append(sentence[i])
                elif obstates[i] == 'e':
                    word.append(sentence[i])
                    item = ''.join(word)
                    del word[:]
                    yield item
                    
                else:
                    raise NameError , '分词状态出现错误 ！ %s' % obstates[i]
            if len(word):
                yield ''.join(word)


    def segment(self, sentence):
        if not sentence:
            return []
        words = []
        for sen in self.__split(sentence.strip()):
            words.extend(self.__segment(sen))
        return words