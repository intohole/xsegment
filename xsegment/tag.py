# coding=utf-8
#!/usr/bin/env python

from collections import defaultdict
import sys
import os
import json
import re
reload(sys)
sys.setdefaultencoding('utf-8')


class HSpeech(object):
    __start_state = None
    __emission_probability = None
    __transition_probability = None
    __states = None
    __min_value = 0.000000000001

    def __init__(self,
                 model=os.path.join(
                     os.path.abspath(os.path.dirname(__file__)), 'dict/')):
        self.__load(model)

    def __load(self, path):
        if path:
            if not path.endswith('/'):
                path = path + '/'
            with open('%s%s' % (path, 'tag_start_state.dat')) as f:
                self.__start_state = json.loads(f.readline())
            with open('%s%s' % (path, 'tag_emission_probability.dat')) as f:
                self.__emission_probability = json.loads(f.readline())
            with open('%s%s' % (path, 'tag_transition_probability.dat')) as f:
                self.__transition_probability = json.loads(f.readline())
            with open('%s%s' % (path, 'tag_obs_status.dat')) as f:
                j = json.loads(f.readline())
                self.__states = [__key for __key in j.keys()]

    def __viterbi(self, obs):
        '''
        特比算法 摘自wiki 维特比算法
        '''
        # print obs
        V = [{}]
        path = {}
        for y in self.__states:
            if self.__emission_probability[y].has_key(obs[0]):
                V[0][y] = self.__start_state[y] * \
                self.__emission_probability[y][obs[0]]
            else:
                V[0][y] = self.__start_state[y] * self.__min_value
            path[y] = [y]
        for t in range(1, len(obs)):
            V.append({})
            newpath = {}
            for y in self.__states:
                prob = 0.
                state = self.__states[0]
                for y0 in self.__states:
                    if self.__emission_probability[y].has_key(obs[t]):
                        __prob = V[t - 1][y0] * self.__transition_probability[
                            y0][y] * self.__emission_probability[y][obs[t]]
                    else:
                        __prob = V[t - 1][y0] * self.__transition_probability[
                            y0][y] * self.__min_value
                    if __prob > prob:
                        prob = __prob
                        state = y0
                V[t][y] = prob
                newpath[y] = path[state] + [y]
            path = newpath
        (prob, state) = max([(V[len(obs) - 1][y], y) for y in self.__states])
        return (prob, path[state])

    def tag(self, segment_words, split_word=' '):
        '''
        功能：
               词性标注
        参数：
               segment_words ， 分词结果
               如果类型为字符串 ， 必须以空格或者tab键为分隔符的字符串
               如果类型不为list ， tuple ， 则抛出异常
        算法：
               hmm 维特比算法
        return 如果句子为空或者None 则返回空的list
               否则，返回[(分词1，词性),(分词2，词性)....(分词n，词性n)]
        '''
        if segment_words:
            if isinstance(segment_words, str):
                segment_words = segment_words.decode('utf-8').split(split_word)
            elif isinstance(segment_words, unicode):
                segment_words = segment_words.split(split_word)
            elif not isinstance(segment_words, (list, tuple)):
                raise Exception, 'type erro!'
            state = self.__viterbi(segment_words)[1]
            return [(segment_words[i], state[i])
                    for i in range(len(segment_words))]
        return []  #如果返回none ， 会造成不必要的判断和错误
