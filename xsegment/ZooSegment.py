# coding=utf-8
#!/usr/bin/env python

from Trie import Trie
import filetutil
import PreSegment
import os
from hmm import HSegment


class Segment(object):

    def segment(self, words):
        pass


class SMM(Segment):

    word_dict = Trie()  # 词典树

    def __init__(self, dictpath=os.path.join(os.path.abspath(os.path.dirname(__file__)),  'dict/dict.txt'), maxlength=8):
        self.word_dictpath = dictpath
        self.maxlength = maxlength
        self.__load_word_dict()

    def __load_word_dict(self):
        contents = filetutil.read_file_strip(self.word_dictpath)
        for word in contents:
            wordarry = word.split()
            self.word_dict.add(wordarry[0].decode('utf-8'), wordarry[1])

    def signal_word_in(self, words):
        count = 0
        for word in words:
            if len(word) == 1:
                count = count + 1
        return count

    def segment(self, words):
        _segmentwords = []
        words = words.decode("utf-8")
        for word in PreSegment.token(words):
            _words = self._segment(word)
            if isinstance(_words, list):
                _segmentwords.extend(_words)
            else:
                _segmentwords.append(_words)
        return _segmentwords

    # 解析中文分词
    def _znsegment(self, words):
        pass

    #
    def _segment(self, words):
        if words:
            if words[1] == 'ZN':
                return self._znsegment(words[0])
            else:
                return words[0]
        return ""
import re

class WSegment(object):

    __chinese = re.compile(ur'[\u4e00-\u9f5a]+').split
    def segment(self, words):
        if words:
            if isinstance(words , str):
                words = words.decode('utf-8')
            if isinstance(words , unicode):
                for word in self.__chinese(words):
                    print word



class FMM(SMM):

    def _znsegment(self, words):
        _result = []
        if words and len(words):
            substring = words
            while len(substring):
                subindex = self.maxlength
                if subindex > len(substring):
                    subindex = len(substring)
                token = substring[:subindex]
                rindex = len(token)
                while rindex > 1:
                    if self.word_dict.search(token[:rindex]):
                        break
                    rindex = rindex - 1
                _result.append(token[:rindex])
                substring = substring[len(token[:rindex]):]
        return _result


class RMM(SMM):

    def _znsegment(self, words):
        _result = []
        if words and len(words):
            substring = words
            while len(substring):
                subindex = self.maxlength
                if subindex > len(substring):
                    subindex = len(substring)
                token = substring[-subindex:]
                lindex = 0
                while lindex < (len(token) - 1):
                    if self.word_dict.search(token[lindex:]):
                        break
                    lindex = lindex + 1
                _result.append(token[lindex:])
                substring = substring[:-len(token[lindex:])]
            _result.reverse()

        return _result


class BMM(SMM):

    _fm = None
    _rm = None

    def __init__(self, dictpath=8, maxlength=8):
        SMM.__init__(self, dictpath, maxlength)
        self._fm = FMM(dictpath, maxlength)
        self._rm = RMM(dictpath, maxlength)

    def segment(self, words):
        fwords = self._fm.segment(words)
        rwords = self._rm.segment(words)
        minlen = len(fwords) - len(rwords)
        if minlen > 0:
            return rwords
        elif minlen < 0:
            return fwords
        else:
            diff_signal_word_num = self.signal_word_in(
                fwords) - self.signal_word_in(rwords)
            if diff_signal_word_num > 0:
                return rwords
            elif diff_signal_word_num < 0:
                return fwords
            else:
                return rwords



class MMSegment(Segment):



    def __init__(self , dictpath=  os.path.join(os.path.abspath(os.path.dirname(__file__)),  'dict/dict.txt')  , maxlength=5 ):
        self.__trie = Trie()
        self.__load_dict(dictpath , self.__trie)
        self.maxlength = maxlength
        self.hmm = HSegment()

    def __load_dict(self , dictpath , trie):
        with open(dictpath) as f:
            for line in f.readlines():
                line = line.strip().split()
                trie.add(line[0] , int(line[1]))


    def segment(self , words):
        if words and isinstance(words , basestring) and len(words) > 0 :
            if not isinstance(words , unicode):
                words = words.decode('utf-8')
                lindex = 0
                rindex = min(len(words) , self.maxlength)
                items = []
                unknow = []
                while lindex < len(words):
                    if self.__trie.search(words[lindex : rindex]):
                        if len(unknow):
                            items.extend(self.hmm.segment(''.join(unknow)))
                            del unknow[:]
                        items.append(words[lindex : rindex])
                        lindex = rindex 
                        rindex = min(len(words) , self.maxlength + lindex)
                        continue
                    rindex -= 1
                    if rindex == lindex:
                        unknow.append(words[lindex])
                        lindex += 1
                        rindex = min(len(words) , self.maxlength + lindex)
                if len(unknow):
                    items.extend(self.hmm.segment(''.join(unknow)))
                    del unknow[:]
                return items 
        return []


if __name__ == "__main__":
    # seg = FMM("dict/dict.txt")
    # print " ".join(seg.segment("如果不肯换位体验，能不能让他们失去位子？！否则他们永远不会懂得权力来自人民。 //@人民日报:【想听真话摸实情，不如换位体验】网友建议：请民航部门领导以普通乘客身份，体验飞机晚点的烦恼…...感同身受，换位思考，还有哪些地方需要领导去体验？欢迎补充〜"))
    m = MMSegment()
    print ' '.join(m.hmm.segment('在2015年开端，作为程序员来说！努力是个球！,世界杯 开赛！梅西很犀利!,世界卫生组织宣布！我了个去!梅花盛开在三月!腊月是个神奇的日子！'))
    print ' '.join(m.segment('南京市长江大桥今天竣工！'))
    print ' '.join(m.segment('理想很远大，现实很骨干'))
    print ' '.join(m.segment('做我女朋友好不好?'))
    print ' '.join(m.segment('在2015年开端，作为程序员来说！努力是个球！,世界杯 开赛！梅西很犀利!,世界卫生组织宣布！我了个去!梅花盛开在三月!腊月是个神奇的日子！'))
    print ' '.join(m.segment(''' 
 现向大家征集2015年全年 办公硬件需求，  截至日期：周五（12月12日）15点之前，请大家在规定时间内回复。
   如有需求显示器、笔记本支架、电池、电源 、内存（并符合要求） 的同学，请单独回复我，并且cc经理，同时请经理回复邮件确认即可申请。  
  2015年  三年笔记本到期的同学，为了避免之前统计不周全，有不在以下名单的同学，请单独回复我。
鼠标键盘等小额物品可直接在ite填写申请单，并经理签字领用，不需要提交给我申请。
        '''))