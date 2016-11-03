# coding=utf-8
#!/usr/bin/env python

from Trie import Trie
import filetutil
import PreSegment
from b2 import file2
from b2 import system2
import os
from hmm import HSegment
from b2 import object2
system2.reload_utf8()
import threading

class StaticDict(object2.Singleton):

    _dict_lock = threading.Lock()
    def __init__(self , dictpath= os.path.join(file2.get_caller_dir(),  'dict/dict.txt')):
        with self._dict_lock:
            if hasattr(self,"_init") is False:
                self.__trie = Trie()
                self.__load_dict(dictpath , self.__trie)
                self._init = True

    def __load_dict(self , dictpath , trie):
        import sys
        sys.stderr.write("load dict starting\n")
        with open(dictpath) as f:
            for line in f.readlines():
                line = line.strip().split()
                trie.add(line[0].decode("utf-8") , int(line[1]))
        sys.stderr.write("load dict end \n")

    def get_trie(self):
        return self.__trie

class Segment(object):

    def segment(self, words):
        pass


class SMM(Segment):

    word_dict = Trie()  # 词典树

    def __init__(self, dictpath=os.path.join(file2.get_caller_dir(),  'dict/dict.txt'), maxlength=5):
        self.word_dictpath = dictpath
        self.maxlength = maxlength
        self.load_word_dict(self.word_dictpath)

    def load_word_dict(self , dictpath):

        with open(dictpath) as f:
            for line in f:
                word_array = line.rstrip().split()
                if len(word_array) >= 2:
                    self.word_dict.add(word_array[0].decode('utf-8'), word_array[1])

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



class MMSegment(Segment,object2.Singleton):

    _slock = threading.Lock()
    def __init__(self , dictpath= os.path.join(file2.get_caller_dir(),  'dict/dict.txt'), maxlength=5 ):
        with self._slock:
            if hasattr(self,"_init") is False:
                self.__trie = StaticDict(dictpath)
                self.maxlength = maxlength
                self.hmm = HSegment()
                self._init = True

    def __load_dict(self , dictpath , trie):
        import sys
        sys.stderr.write("load dict starting\n")
        with open(dictpath) as f:
            for line in f.readlines():
                line = line.strip().split()
                trie.add(line[0].decode("utf-8") , int(line[1]))
        sys.stderr.write("load dict end \n")

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

class BMMSegment(MMSegment):



    def segment(self , words):
        if words and isinstance(words , basestring) and len(words) > 0 :
            if not isinstance(words , unicode):
                words = words.decode('utf-8')
            rindex = len(words) -1
            lindex = max(0 , len(words) - self.maxlength)
            items = []
            unknow = []
            while rindex >=0:
                if self.__trie.search(words[lindex : rindex]):
                    if len(unknow):
                        items.extend(self.hmm.segment(''.join(unknow)))
                        del unknow[:]
                    items.append(words[lindex : rindex])
                    rindex = lindex
                    lindex = max(0 , len(words) - self.maxlength)
                    continue
                lindex += 1
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
    m = MMSegment()
    d = MMSegment()
