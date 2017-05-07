zoo-segment 中文分词python分词
=================
思想
------------------------
*正向最大匹配  
*逆向最大匹配  
*词典树  
*hmm分词  
*正则预分词  
```python

       	from xsegment.ZooSegment import * 
       	from xsegment.hmm import HSegment 
       	seg = FMM() #前向最大匹配分词 
	   	seg = RMM() #后向最大匹配分词
		seg = MMSegment() #hmm识别未识别词匹配
       	print " ".join(seg.segment(  "如果不肯换位体验，能不能让他们失去位子？！否则他们永远不会懂得权力来自人民。 //@人 民日报:【想听真话摸实情，不如换位体验】网友建议：请民航部门领导以普通乘客身份  ，体验飞机晚点的烦恼…...感同身受，换位思考，还有哪些地方需要领导去体验？欢迎补充〜")  )  #如果 不肯 换位 体验 ， 能不能 让 他们 失去 位子 ？！ 否则 他们 永远 不会 懂得 权力 来自 人民 。 //@人民日报 :【 想 听 真话 摸 实情 ， 不如 换位 体验 】 网友 建议 ： 请 民航 部门 领导 以 普通 乘客 身份 ， 体验 飞机 晚点 的 烦恼 …... 感同身受 ， 换位 思考 ， 还有 哪些地方 需要 领导 去 体验 ？ 欢迎 补充 〜

```


中文拼音支持
---------------------
```python
          
          p = pinyin()  
          print p.pinyin_segment('12上帝3aa') #12 shang di 3aa 
          print p.pinyin_segment('12上帝3aa' ,'#') #  'shang#di#3aa  
          会自动提取汉字进行转换  
          print p.zh2pinyin('我爱a') # wo ai a 不会自动转换不是汉字  
          print p.zh2pinyin('我爱a' , '#') # wo#ai#a


情感极性简单分析
---------------------
```python


     from psentiment import SentimentTrie

     sentiment = SentimentTrie()
     print sentiment.get_word_sentiment('断章取义') # 返回值 -1.2 情感为负
     print sentiment.get_words_sentiment(['我' , '喜欢' , '你']) #[('\xe6\x88\x91', 1.7499999999999998), ('\xe5\x96\x9c\xe6\xac\xa2', 1.4310722100656499), ('\xe4\xbd\xa0', -0.7)] 返回每个词的极值
     print sentiment.get_sentence_sentiment(['我' , '喜欢' , '你']) # 返回2.48107221007 情感为积极
     print sentiment.get_sentence_sentiment(['我' , '恨' , '你']) #-0.4392 情感为消极
```

词性标注
----------------------
* hmm
```python
      

      from xsegment.tag import HSpeech  
      print h.tag('我 早饭 我 的 祖国 !')  
      print h.tag('xsegment')   
```

关键词提取
-----------
* textrank  

```python
      
      from xsegment.textrank import TextRank1
      k = TextRank1.create_word_window(分词结果, 7 , weight = True)
      scoremap = TextRank1.textrank(k , iter_count = 100)
      for i in TextRank1.sort_score(scoremap , 12):
          print i[0], i[1]
```
* tfidf
```python
	from xsegment.tfidf import TfIdf
	tfidf = TfIdf("idf.file")
	# 训练过程
	tfidf.add("a b c d")
	tfidf.add("a b c c d")
	tfidf.add("a a a b")
	tfidf.add("a")
	tfidf.add("a c")
	tfidf.train()
	tfidf.save()
	tfidf.calc("a b b")
```
		

词语义距离
--------------
+ 基于哈工大开源词林词典实现（词典已经很久没更新，使用word2vec会更加好一点？）


```python

	from xsegment.wordsim import WordSim
	wordsim = WordSim()
	wordsim.word_sim("你" , "我" ， desc = True) #返回词之间距离数组 ， 按照降序排列 ， 升序 desc = False
```
自动摘要
-------------
+ 基于自然语言摘要
+ 基于textrank自动摘要

```python

	from xsegment.summary import SimpleSummary
	from xsegment.summary import TextRankSummary
	summary = SimpleSummary() #TextRankSummary()
	summary.summary("文章内容" , "标题" ) #返回摘要
```
Simhash文本相似计算
------------

```python
			>>> from xsegment.simhash import SimHash
	        >>> def segfun(words):
            ...     return [ words[i:i+2] for i in range(len(words) - 1)]
            >>> s = SimHash( segfun = segfun)
            >>> s.figureprint("abc") == s.figureprint("abc")
            >>> s.figureprint("abc") == s.figureprint("abcd")
            >>> s.distance(s.figureprint("abc") , s.figureprint("abcde"))
```

文档相似度计算
----------------
+ 余弦算法


```python
		from xsegment.similar import consine
		consine("我 的 中国 是 伟大 的" , "我 爱 我 的 祖国" , split_fun = lambda x: x.split())
```

多文档相似度
------------


```python
	
		from xsegment.vsm import Vector
		v = Vector()
    	v.add_doc('a', 'a b c d c a')
    	v.add_doc('b', 'a b c d c a')
    	v.add_doc('c', 'c d f e r a c')
    	# print v.totfidf()
    	print v.similarty('a', 'b')
```

挖掘新词  	
--------------


```python

    python xsegment/word_rec.py -i [文件/路径] 
```
