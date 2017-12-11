# coding=utf-8
#!/usr/bin/env python

from b2.ds2 import DTrie
import PreSegment
from b2 import file2
from b2 import system2
import os
from hmm import HSegment
from b2 import object2
system2.reload_utf8()
import threading
import re


class StaticDict(object2.Singleton):
    """词典单例状态 确保词典单词加载
    """
    _dict_lock = threading.Lock()

    def __init__(self,
                 dictpath=os.path.join(file2.get_caller_dir(),
                                       'dict/dict.txt')):
        with self._dict_lock:
            if hasattr(self, "_init") is False:
                self._trie = DTrie()
                self.__load_dict(dictpath, self._trie)
                self._init = True

    def __load_dict(self, dictpath, trie):
        import sys
        sys.stderr.write("load dict starting\n")
        with open(dictpath) as f:
            for line in f:
                line = line.strip().split()
                trie.add(line[0].decode("utf-8"), int(line[1]))
        sys.stderr.write("load dict end \n")

    def get_trie(self):
        return self._trie


class Segment(object):
    def segment(self, words):
        pass


class MMSegment(Segment, object2.Singleton):

    _slock = threading.Lock()

    def __init__(self,
                 dictpath=os.path.join(file2.get_caller_dir(),
                                       'dict/dict.txt'),
                 maxlength=5):
        with self._slock:
            if hasattr(self, "_init") is False:
                tree_dict = StaticDict(dictpath)
                self._trie = tree_dict.get_trie()
                self.maxlength = maxlength
                self.hmm = HSegment()
                self._init = True

    def __load_dict(self, dictpath, trie):
        import sys
        sys.stderr.write("load dict starting\n")
        with open(dictpath) as f:
            for line in f.readlines():
                line = line.strip().split()
                trie.add(line[0].decode("utf-8"), int(line[1]))
        sys.stderr.write("load dict end \n")

    def segment(self, words):
        if words and isinstance(words, basestring) and len(words) > 0:
            if not isinstance(words, unicode):
                words = words.decode('utf-8')
            lindex = 0
            rindex = min(len(words), self.maxlength)
            items = []
            unknow = []
            while lindex < len(words):
                if self._trie.contain(words[lindex:rindex]):
                    if len(unknow):
                        items.extend(self.hmm.segment(''.join(unknow)))
                        del unknow[:]
                    items.append(words[lindex:rindex])
                    lindex = rindex
                    rindex = min(len(words), self.maxlength + lindex)
                    continue
                rindex -= 1
                if rindex == lindex:
                    unknow.append(words[lindex])
                    lindex += 1
                    rindex = min(len(words), self.maxlength + lindex)
            if len(unknow):
                items.extend(self.hmm.segment(''.join(unknow)))
                del unknow[:]
            return items
        return []


class BMMSegment(MMSegment):
    def segment(self, words):
        if words and isinstance(words, basestring) and len(words) > 0:
            if not isinstance(words, unicode):
                words = words.decode('utf-8')
            rindex = len(words) - 1
            lindex = max(0, len(words) - self.maxlength)
            items = []
            unknow = []
            while rindex >= 0:
                if self._trie.contain(words[lindex:rindex]):
                    if len(unknow):
                        items.extend(self.hmm.segment(''.join(unknow)))
                        del unknow[:]
                    items.append(words[lindex:rindex])
                    rindex = lindex
                    lindex = max(0, len(words) - self.maxlength)
                    continue
                lindex += 1
                if rindex == lindex:
                    unknow.append(words[lindex])
                    lindex += 1
                    rindex = min(len(words), self.maxlength + lindex)
            if len(unknow):
                items.extend(self.hmm.segment(''.join(unknow)))
                del unknow[:]
            return items
        return []


if __name__ == "__main__":
    m = MMSegment()
    for word in m.segment('我的老家在东北那嘎子'):
        print word.encode("utf-8")
    d = MMSegment()
