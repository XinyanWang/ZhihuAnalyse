# -*- coding:utf-8 -*-
import re,time,pickle,requests
from BeautifulSoup import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from lxml import etree

import zhihu_tools as tools
import UserInfos





def bridge(tp):

    print 'working...'
    try:
        t=UserInfos.User(tp[0],tp[1])
    except requests.ChunkedEncodingError,e:
        try:
            t=UserInfos.User(tp[0],tp[1])
        except requests.ChunkedEncodingError,e:
            try:
                t=UserInfos.User(tp[0],tp[1])
            except requests.ChunkedEncodingError,e:
                t=None
                print 'ChunkedEncodingError'
    print 'done'
    return t
   

def logintools(tp):
    return tools.newlogin(tp[0],tp[1])


def setsessions():
    infos=[
       ('wangxy940930@gmail.com','WXY940930'),
#       ('2824935672@qq.com','WXY940930'),
       ('k64_cc@163.com','WXY940930'),
       ('chh_cc@yeah.net','WXY940930'),
       ('owenclan@163.com','WXY940930'),
       ('jiangjiaqingmiao@163.com','WXY940930'),
       ('jiangjiaqingmiao@126.com','WXY940930'),
       ('zhihubot1@163.com','WXY940930'),
       ('zhihubot2@163.com','WXY940930'),
       ('zhihubot3@163.com','WXY940930')
#       ,('zhihubot4@163.com','WXY940930')
#       ,('zhihubot5@163.com','WXY940930')
#       ,('zhihubot6@163.com','WXY940930')
#       ,('zhihubot7@163.com','WXY940930')
#       ,('zhihubot8@163.com','WXY940930')
#       ,('zhihubot9@163.com','WXY940930')
#       ,('zhihubot10@163.com','WXY940930')
#       ,('zhihubota@163.com','WXY940930')
       ]


    pool=ThreadPool(9)

    sessions=pool.map(logintools,infos)

    pool.close()
    pool.join()

    print 'Log in success'
    return sessions


def spider(filename,sessions,start=None,end=None):

    f=open(filename)
    homepages=pickle.load(f)[start:end]
    f.close()
    #读取主页列表

    print 'Task Start'
    workers=[]
    for i in range(len(homepages)/9+1):
        workers+=sessions
    print len(homepages),len(workers)

    pool=ThreadPool(7)

    results=pool.map(bridge,zip(workers,homepages))

    pool.close()
    pool.join()

    print 'saving...'
    f=open('124173_'+str(start)+'-'+str(end)+'.data','w')
    for i in results:
        pickle.dump(i.infos,f)
    f.close()
    print 'Task End'
    print time.localtime()






#print 'We have two functions. First, you should use setsessions() to get workers for your spider. Then you can use spider() to download infos from Internet.'
#sessions=setsessions()
#i=16000
#while True:
#    spider('p1_124173_num.data',sessions,start=i,end=i+2000)
#    i+=2000
#    if i>124173:
#        spider('p1_124173_num.data',sessions,start=i-2000)
#        break
    
