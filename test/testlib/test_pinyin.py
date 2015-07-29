#coding=utf-8


from xsement.pinyin import pinyin

if __name__ == '__main__':
    p = pinyin()
    print p.pinyin_segment(u'上帝 3aa','#')
    print p.zh2pinyin('上帝aa')