#coding=utf-8

import chardet


class Sentence(object):
    """句子信息存储结构体
        oristring 原始句内容
        index 原始句的位置
        loc 段落中的位置
        items 分词信息
        keywords 关键词数目
        score 关键句打分
        words 分词
        wordLen 句子含有的词数目　
    """

    def __init__(self,
                 oristring,
                 index,
                 loc,
                 words=None,
                 items=None,
                 keywords=None,
                 wordLen=0,
                 score=0.):
        self.index = index
        self.items = items
        self.score = score
        self.keywords = keywords
        self.oristring = oristring
        self.loc = loc
        self.words = words
        self.wordLen = wordLen

    def __str__(self):
        # 返回字符串功能　str()
        msg = []
        for __key, __val in self.__dict__.items():
            if isinstance(__val, (list, tuple)):
                msg.append('[ %s %s ]' %
                           (__key, ' '.join([str(__v) for __v in __val])))
            else:
                msg.append('[ %s %s ]' % (__key, __val))
        return '\n'.join(msg)


def split_sentence(self, content, split):
    """对输入的文本切分句子
    """
    if content is not None and isinstance(content, basestring):
        code = chardet.detect(content)
        if code["encoding"].lower() != "utf-8":
            content.encode(code["encoding"]).decode("utf-8")
        sentences = []
        index = 0
        for pagraph in content.split(split):  # 段落分隔符　是/r/n
            loc = ITEM_LOCATION.MEDIM
            split_last = 0
            save_sentences_len = len(sentences)
            pagraph = pagraph.strip()
            for i in range(len(pagraph)):
                if pagraph[i] in ['!', '！', '?', '？', ';', '；']:
                    index = index + 1
                    sentences.append(
                        Sentence(pagraph[split_last:i + 1], index, loc))
                    split_last = i + 1
                if pagraph[i] == '。':
                    if i > 1:
                        if pagraph[i - 1] in [
                                '１', '２', '３', '４', '５', '６', '７', '８', '９',
                                '０'
                        ]:
                            if ((i + 1) < len(pagraph)) and pagraph[i + 1] in [
                                    '１', '２', '３', '４', '５', '６', '７', '８',
                                    '９', '０'
                            ]:
                                continue
                    index = index + 1
                    sentences.append(
                        Sentence(pagraph[split_last:i + 1].strip(), index,
                                 loc))
                    split_last = i + 1
            if split_last != len(pagraph):
                sentences.append(
                    Sentence(pagraph[split_last:], index, ITEM_LOCATION.END))
            if len(sentences) > save_sentences_len:
                sentences[save_sentences_len].loc = ITEM_LOCATION.BEGIN
            if len(sentences) > (save_sentences_len + 1):
                sentences[-1].loc = ITEM_LOCATION.END
        return sentences
    return []
