# coding=utf-8



from copy import copy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')




'''
自动摘要 编写
'''


def enum(args, start=0):
    '''
    enum 枚举实现　－　＞　使用方式　　enmu('ENUM1 ... Enum2 .. EnumN')

    '''
    class Enum(object):
        __slots__ = args.split()

        def __init__(self):
            for i, key in enumerate(Enum.__slots__, start):
                setattr(self, key, i)

    return Enum()

ITEM_LOCATION = enum('BEGIN MEDIM END NONE')  # 位置变量


class WordItem(object):

    def __init__(self, word, tag, isKeyWord=False):
        self.word = word
        self.tag = tag
        self.isKeyWord = isKeyWord

    def __str__(self):
        msg = []
        for __key, __val in self.__dict__.items():
            if isinstance(__val, (list, tuple)):
                msg.append('%s %s' %
                           (__key, ' '.join([str(__v) for __v in __val])))
            else:
                msg.append('[%s %s]' % (__key, __val))
        return ' '.join(msg)


class Sentence(object):

    '''
    句子对象 ：
    oristring 原始句内容
    index 原始句的位置
    loc 段落中的位置
    items 分词信息
    keywords 关键词数目
    score 关键句打分
    words 分词
    words_len 句子含有的词数目　
    '''

    def __init__(self, oristring, index, loc, words=None, items=None, keywords=None, words_len=0, score=0.):
        self.index = index
        self.items = items
        self.score = score
        self.keywords = keywords
        self.oristring = oristring
        self.loc = loc
        self.words = words
        self.words_len = words_len

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


class Summary(object):

    '''
    基于新闻的摘要功能　
    主要提取新闻关键句子　按照文章顺序输出

    '''

    min_sentence_len = 8
    max_sentence_len = 25

    def __init__(self):
        raise NotImplementedError , 'no implement this func 【%s】' % sys._getframe().f_code.co_name

    def summary(self, content, title, summary_sentences=5, pagraph_split='\r\n'):
        '''
        摘要主要接口
        content  新闻
        title 新闻的标题
        summary_sentences 返回的句子数目
        '''
        # 是否要把标题作为句子切分　有待考虑
        sentences = self.split_sentence(title, pagraph_split)
        # 分割句子　－＞　将文本分割为　Sententce　ｌｉｓｔ
        sentences.extend(self.split_sentence(content, pagraph_split))
        self.segment(sentences)  # 分词　将所有句子对象转换为分词
        self.extractKeyWord(sentences, topN=30)  # 抽取关键词　
        self.score_sentences(sentences)  # 根据　句子信息对文章打分
        # 根据句子得分高低排序　得分高的在前面
        sentences = self.sentences_filter(sentences, 'score', reverse=True)
        summary_len = self.get_summary_len(len(sentences) ,  summary_sentences)

        # if len(sentences) > summary_sentences:  # 判断　是否超过需要的句子数目
        sentences = sentences[: summary_len]  # 句子数目
        sentences = self.sentences_filter(sentences, 'index')
        return (title, sentences)

    def get_summary_len(self,  sentences_length, summary_sentences):
        '''
        设置摘要的大小
        如果为整数 ， 
            判断是否大于句子长度 ， 如果是返回设置的长度 ， 否则返回 判断是否大于句子长度
        如果为浮点数 ， 计算 句子数目 *取得比率 ， 判断计算的长度是否小于最小限制
        '''
        if isinstance(summary_sentences, (float, int)):
            if summary_sentences > 1:
                return summary_sentences if summary_sentences <= sentences_length else sentences_length
            elif summary_sentences > 0:
                summary_calc_len = int(sentences_length * summary_sentences)
                if summary_calc_len < self.min_sentence_len:
                    if self.min_sentence_len > sentences_length:
                        return sentences_length
                    return self.min_sentence_len

                if summary_calc_len > self.max_sentence_len:
                    if self.max_sentence_len > sentences_length:
                        return sentences_length
                    return self.max_sentence_len
                return summary_calc_len
        raise TypeError, 'summary_sentences must be is int or folat '

    def split_sentence(self, content, split):
        '''
        对输入的文本切分句子

        '''
        if content:
            if isinstance(content, str):
                content = content.decode('utf-8')
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
                            Sentence(pagraph[split_last: i + 1], index, loc))
                        split_last = i + 1
                    if pagraph[i] == '。':
                        if i > 1:
                            if pagraph[i - 1] in ['１', '２', '３', '４', '５', '６', '７', '８', '９', '０']:
                                if ((i + 1) < len(pagraph)) and pagraph[i + 1] in ['１', '２', '３', '４', '５', '６', '７', '８', '９', '０']:
                                    continue
                        index = index + 1
                        sentences.append(
                            Sentence(pagraph[split_last: i + 1].strip(), index, loc))
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

    def segment(self, sentences):
        '''
        content : 每个要分词
        返回值：
        '''
        raise NotImplementedError , 'no implement this func 【%s】' % sys._getframe().f_code.co_name

    def extractKeyWord(self, sentences, topN=20):
        '''
        抽取关键词接口
        '''
        raise NotImplementedError , 'no implement this func 【%s】' % sys._getframe().f_code.co_name

    def score_sentences(self, sentences):
        '''
        每个句子单独打分
        '''
        for i in range(len(sentences)):
            sentences[i].score = self.score(sentences[i])

    def score(self, sentence):
        '''
        单句打分
        '''
        raise NotImplementedError , 'no implement this func 【%s】' % sys._getframe().f_code.co_name

    def sentences_filter(self, sentences, order=None, reverse=False):
        '''
        sentences : 每个文档的句子集合
        score : 阈值
        返回值: sentences
        '''
        if sentences:
            if isinstance(sentences, list) and len(sentences) > 0:
                return sorted(sentences, key=lambda x: getattr(x, order), reverse=reverse)
        raise TypeError, 'sentences must be list and item is sententce'



class WeightArray(object):

    def __init__(self, datas, distance_fun):
        self.lable_dict = {datas[index][0]:index   for index in range(len(datas))}
        self.distance_map = self.create_distance_map(datas, distance_fun)
        self.data_len = len(datas)




    def __getitem__(self, label_tuple):
        label1, label2 = label_tuple
        if self.lable_dict.has_key(label1) and self.lable_dict.has_key(label2):
            index1 = self.lable_dict[label1]
            index2 = self.lable_dict[label2]
            return self.get_distance_by_index(index1 , index2)
        raise IndexError, 'index : %s , index2 : %s  not in this distance_map'



    def get_distance_by_index(self  , row , line ):
        '''
        function:
            下半角矩阵 ， 转换坐标

        '''
        if line > row :
            tmp = row 
            row = line 
            line = tmp  
        return self.distance_map[row][line]



    def create_distance_map(self, datas, distance_fun):
        '''
        function:
            创建数据距离map
        params:
            datas 数据，格式 [[label1 , x1 ,x2...,xN ] , [lable2 , x1 , x2 , ..., xN]....[labelN , x1, x2 , ...xN] ]
        return 
            datas_map 
        '''
        distance_map = []
        for i in range(len(datas)):
            tmp_distance = []
            for j in range(i + 1):
                if i == j:
                    tmp_distance.append(0)
                else:
                    tmp_distance.append(distance_fun(datas[i], datas[j]))
            distance_map.append(tmp_distance)
        return distance_map




class TextRankSummary(Summary):

    """docstring for TextRankSummary"""

    def __init__(self , d = 0.85 , threshold = 0.05 ,iter_count = 100 ):
        super(TextRankSummary, self).__init__()

        self.d = d #阻尼系数
        self.iter_count = iter_count #迭代次数
        self.threshold = threshold #阈值 ， 设置此值后 ， 在计算rank的时候，如果小于这个数值时，跳出迭代







    def summary(self, content, title, summary_sentences=5, pagraph_split='\r\n'):
        raise NotImplementedError , 'no implement this func 【%s】' % sys._getframe().f_code.co_name




    def rank(self , iter_count  , threshold ,sentence_weight_map , sentence_len , d = 0.8  ):
        '''
        功能:
            param1 
                sentence_distance_map 句子相似度矩阵
                sentence_len 句子总数
            return 
                sentences_score  句子权重值打分
        '''
        #初始化句子权重 ，暂时定位1 
        sentences_score = [ 1 - d   for i in  len(range(sentence_len))]
        sentence_out_sum = [] # 每个句子出链的权重比值
        for i in range(sentence_len):
            sentence_out_sum[i] = sum(sentence_weight_map[(i , j )] for j in range(sentence_len))

        
        #weight_sum 
        for _ in range(iter_count):
            tmp_score = copy(sentences_score)
            max_diff = None 
            for i in range(sentence_len):
                #所有句子都是入链
                for j in range(sentence_len):
                    if i == j:
                        continue
                    tmp_score[i] +=  d * sentence_weight_map[(i , j )] / sentence_out_sum[j] * sentences_score[j] 
                diff = math.abs( tmp_score[i] - sentences_score[i] )
                if max_diff == None or diff > max_diff:
                    max_diff = diff 
            sentences_score = tmp_score
            if max_diff  < threshold:
                break 

        return sorted([(sentences_score , i )  for i in range(sentence_len) ] , key =lambda x : x[0] , reversed = True) 

    def segment(self, sentences):
        for sentence in sentences:
            sentence.words = [ sentence.oristring[i : i + 2] for i in range( len(self.__segment.segment(sentence.oristring) - 2)]
            sentence.words_len





    def get_sentence_distance(self  , sentence_item1 , sentence_item2 ):
        raise NotImplementedError
        





if __name__ == '__main__':
    # summary = Summary()
    # print summary.get_summary_len(20 , 0.5)
    s = SimpleSummary()
    x = None
    with open('d:/feiji') as f:
        x = ''.join([line for line in f.readlines() if line.strip() != ''])
    with open('d:/summary.txt' , 'w') as f:
        for i in s.summary(x, '康佳携手万合天宜启动新生代历练计划', summary_sentences=0.08)[1]:
            f.write(i.oristring + "\n")



