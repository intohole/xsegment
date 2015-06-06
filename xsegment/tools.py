#coding=utf-8


class SegmentTrain(object):
    state = defaultdict(float)
    __states = ['s', 'm', 'b', 'e']
    # 为了防止被 0 除 出现异常 ， 则每个状态初始化为1。
    # 开始状态矩阵构建
    __start_state = {'s': 1., 'b': 1., 'm': 1., 'e': 1.}
    # 隐藏状态转移
    __transition_probability = {
        's': {'s': 1.,  'b': 1., 'm': 1., 'e': 1.}, 'b': {'s': 1.,  'b': 1., 'm': 1., 'e': 1.},
'm': {'s': 1.,  'b': 1., 'm': 1., 'e': 1.}, 'e': {'s': 1.,  'b': 1., 'm': 1., 'e': 1.}}
    # 隐藏状态下各个观察状态发生频率
    __emission_probability = {'s': defaultdict(float), 'e': defaultdict(
        float), 'b': defaultdict(float), 'm': defaultdict(float)}

    word_state = set()

    def save_state(self):
        with open('start_state.txt', 'w') as f:
            f.write(json.dumps(self.__start_state))
        with open('emission_probability.txt', 'w') as f:
            f.write(json.dumps(self.__emission_probability))
        with open('transition_probability.txt', 'w') as f:
            f.write(json.dumps(self.__transition_probability))

    def add_line(self, line):
        if not (line and isinstance(line, (str, unicode)) and line != ''):
            raise Exception, line
        text_arry = line.strip().split()
        if len(text_arry[0].decode('utf-8')) > 1:
            self.__start_state['b'] += 1
        else:
            self.__start_state['s'] += 1
        word_label = []  # 保存单词标签 ， 单词 （位置标记 ， 词）
        for word in text_arry:
            word = word.decode('utf-8')  # 因为汉字是utf-8
            word = word.strip()
            if len(word) == 1:
                word_label.append(('s', word))
            elif len(word) == 2:
                word_label.append(('b', word[0]))
                word_label.append(('e', word[1]))
            elif len(word) > 2:
                word_label.append(('b', word[0]))
                for mid_word in word[1:-1]:
                    word_label.append(('m', mid_word))
                word_label.append(('e', word[-1]))
         # 2元文法
        for i in range(len(word_label) - 1):
            self.__transition_probability[
                word_label[i][0]][word_label[i + 1][0]] += 1
        # 循环整个标记
        for i in range(len(word_label)):
            self.word_state.add(word_label[i][1])
            self.state[word_label[i][0]] += 1
            self.__emission_probability[
                word_label[i][0]][word_label[i][1]] += 1

    def train(self, content = []):
        for line in content:
            self.add_line(line)
        self.translte()

    def translte(self):
        '''
        有状态数量转换为概率
        '''
        # 初始化矩阵数目
        __start_state_count = 0
        for __value in self.__start_state.values():
            __start_state_count += __value
        # 计算开始状态概率
        for __key in self.__start_state.keys():
            self.__start_state[__key] = self.__start_state[
                __key] / __start_state_count
        # 初始化矩阵概率运算完毕

        # 转移矩阵
        for __state in self.__transition_probability.keys():
            for __afther_state in self.__transition_probability[__state].keys():
            # 计算公式 =》 p(Cj | Ci) = count(Ci,Cj) / count(Ci)
                self.__transition_probability[__state][__afther_state] = self.__transition_probability[
                    __state][__afther_state] / self.state[__state]

         # 观察状态发生时候 隐藏状态发生概率
        for __hide in self.__emission_probability.keys():
            for word in self.word_state:
                self.__emission_probability[__hide][word] = (
                    self.__emission_probability[__hide][word] + 1) / self.state[__hide]



class TagTrain(object):
    __start_state = defaultdict(float)
    __obs_status = defaultdict(float)
    # 为了防止被 0 除 出现异常 ， 则每个状态初始化为1。
    # 开始状态矩阵构建
    # 隐藏状态转移
    tag_find = re.compile('/[a-z]+').finditer
    __transition_probability = {}
    # 隐藏状态下各个观察状态发生频率
    __emission_probability = {}

    word_state = set()

    def save_state(self):
        with open('tag_start_state.dat', 'w') as f:
            f.write(json.dumps(self.__start_state))
        with open('tag_emission_probability.dat', 'w') as f:
            f.write(json.dumps(self.__emission_probability))
        with open('tag_transition_probability.dat', 'w') as f:
            f.write(json.dumps(self.__transition_probability))
        with open('tag_obs_status.dat', 'w') as f:
            f.write(json.dumps(self.__obs_status))
        

    def add_line(self, line):
        if not (line and isinstance(line, (str, unicode)) and line != ''):
            raise Exception, line
        tag_arry =[label for label in [ __tag.split('/') for __tag in line.strip().split()] if len(label) > 1 and label[1] != '' and label[0] != "" ]
        if len(tag_arry) < 0:
            return
        try:
            self.__start_state[tag_arry[0][1]] += 1.
        except Exception,e:
            print e
        for i in range(1 , len(tag_arry)):
            if not self.__transition_probability.has_key(tag_arry[i][1]):
                self.__transition_probability[tag_arry[i][1]] = defaultdict(float)
            self.__transition_probability[tag_arry[i][1]][tag_arry[i-1][1]] += 1
        for __tag in tag_arry:
            self.word_state.add(__tag[0])
            self.__obs_status[__tag[1]] += 1
            if not self.__emission_probability.has_key(__tag[1]):
                self.__emission_probability[__tag[1]] = defaultdict(float)
            self.__emission_probability[__tag[1]][__tag[0]] += 1

    def train(self, file_name):
        with open(file_name) as f:
            for line in f.readlines():
                self.add_line(line)
        self.translte()

    def translte(self):
        '''
        有状态数量转换为概率
        '''
        # 初始化矩阵数目
        __start_state_count = 0
        for __key in self.__obs_status:
            self.__start_state[__key] += 0.

        for __value in self.__start_state.values():
            __start_state_count += __value
        # 计算开始状态概率
        for __key in self.__start_state.keys():
            self.__start_state[__key] = self.__start_state[
                __key] / __start_state_count
        # 初始化矩阵概率运算完毕

        # 转移矩阵
        for __state in self.__transition_probability.keys():
            for __afther_state in self.__obs_status.keys():
            # 计算公式 =》 p(Cj | Ci) = count(Ci,Cj) / count(Ci)
                self.__transition_probability[__state][__afther_state] = (self.__transition_probability[
                    __state][__afther_state] + 1.0)/ (self.__obs_status[__state] + 1.0)

         # 观察状态发生时候 隐藏状态发生概率
        for __hide in self.__emission_probability.keys():
            for word in self.__emission_probability[__hide].keys():
                try:
                    self.__emission_probability[__hide][word] = (
                    self.__emission_probability[__hide][word] + 1) / (self.__obs_status[__hide] + 1)
                except Exception,e:
                    print __hide


if __name__ == '__main__':
    import os
    import re

    t = SegmentTrain()

    word = re.compile('/[a-z]+\s?')
    diff = set()
    for file_name in os.listdir("d:/data/"):
        file_path = '%s%s' % ('d:/data/' , file_name)
        with open(file_path) as f:
            content = f.readlines()
        try:
            wd = content[2].split('：')[1].strip()
        except Exception,e:
            print file_path , e
        for line in content[6:]:
            line = line.strip().replace('[%s]' % wd , wd).split("\t")[2]
            if line in diff:
                continue
            diff.add(line)
            t.add_line(' '.join(word.split(line)))

    t.translte()
    t.save_state()

    t = TagTrain()
    t.add_line('越南/ns 电视台/n 报道/v 了/u 许多/a 市民/n 因为/c 赌球/v 而/c >输掉/v 了/u 所有/a 金钱/n 的/u 消息/n ，/w 设有/v 电视机/n 的/u 酒吧/n 在/p 直播/v 比赛/v 时/nt 挤/v 得/u 水泄不通/i 。/w')

    word = re.compile('/[a-z]+\s?')
    diff = set()
    for file_name in os.listdir("data/"):
        file_path = '%s%s' % ('data/' , file_name)
        with open(file_path) as f:
             content = f.readlines()
             try:
                 wd = content[2].split('：')[1].strip()
             except Exception,e:
                 print file_path , e
             for line in content[6:]:
                line = line.strip().replace('[%s]' % wd , wd).split("\t")[2]
                if line in diff:
                    continue
                diff.add(line)
                t.add_line(line)
    t.train('pku_training.utf8')
    t.translte()
    t.save_state()
