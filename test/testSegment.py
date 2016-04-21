#coding=utf-8


import os
from xsegment import ZooSegment
from b2 import system2 


if __name__ == '__main__':
    system2.reload_utf8()
    m = ZooSegment.MMSegment()
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
