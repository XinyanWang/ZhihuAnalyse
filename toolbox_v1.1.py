################################
#Zhihu_tools for Analysing
#Finished in 02/14/2015
#Miao~
#Your Gift Is Here~
################################


from lxml import etree
from BeautifulSoup import BeautifulSoup
import re,requests,time




################################
def newlogin(email='zhihubot7@163.com',password='WXY940930'):
    #模拟登陆
    '返回session类'
    post_header={
        'Host':'www.zhihu.com',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
#    'Accept':'image/png,image/*;q=0.8,*/*;q=0.5',
#    'Accept-Language':'zh-Hans-CN,zhHans;q=0.5',
#    'Accept-Encoding':'gzip, deflate',
#    'Referer':'http://www.zhihu.com/',
#    "Cache-Control": "max-age=0",
#    "Connection": "Keep-Alive",
        }
    s=requests.session()
    req_1=s.get('http://www.zhihu.com',headers=post_header)
    #第一次访问,get主页内容

    find_xsrf=BeautifulSoup(req_1.text)
    list_xsrf=find_xsrf.findAll(attrs={
        'type':'hidden',
        'name':'_xsrf'})
    only_xsrf=re.findall('[0-9a-z]{32,}',str(list_xsrf[0]))
    #得到_xsrf


    data={'_xsrf':only_xsrf[0],'email':email,'password':password,'rememberme':'y'}
    req_2=s.post(url='http://www.zhihu.com/login',data=data,headers=post_header)
    #第二次访问，post表单

    return s



################################


def findFollowees(session,homepage):
    #得到用户关注的人
    '输入用户主页，返回关注名单'

    headers={
        'Host':'www.zhihu.com',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
#    'Accept':'image/png,image/*;q=0.8,*/*;q=0.5',
#    'Accept-Language':'zh-Hans-CN,zhHans;q=0.5',
#    'Accept-Encoding':'gzip, deflate',
    'Referer':homepage+'/followees'
#    ,"Cache-Control": "max-age=0",
#    "Connection": "Keep-Alive",
    }
    
    pattern='[0-9a-z]{32}'
    req=session.get(url=homepage+'/followees',headers=headers)
    soup=BeautifulSoup(req.text.encode('utf-8'))
    hashtag=soup(attrs={'class':"zh-general-list clearfix"})
    hash_id=re.findall(pattern,str(hashtag[0]))[0]
    #find hash_id

    tags=soup(name='span',attrs={'class':'zm-profile-section-name'})
    pattern='[0-9]{1,} \xe4'
    followee_num=re.findall(pattern,str(tags[0]))[0]
    followee_num=re.match('[0-9]{1,}',followee_num).group()
    #find followee_num

    _xsrftags=soup(attrs={'type':'hidden','name':'_xsrf'})
    pattern='[0-9a-z]{32}'
    _xsrf=re.findall(pattern,str(_xsrftags))[0]

    firstlist=hashtag[0].findAll(attrs={'class':'zm-profile-card zm-profile-section-item zg-clear no-hovercard'})
    try:
        firstlist=[re.findall(r'people/[0-9a-zA-Z\-_]{1,}',str(item))[0] for item in firstlist]
    except IndexError,e:
        print 'IndexError'
        pass
    firstlist=[item[7:] for item in firstlist]

    allofthem=[]
    if int(followee_num)<=40 and int(followee_num)>20:
        num=int(followee_num)
        postdata={
            'method':'next',
            'params':'''{"offset":'''+str(num)+''',"order_by":"created","hash_id":"'''+hash_id+'''"}''',
            '_xsrf':_xsrf}

    
        st=session.post(url='http://www.zhihu.com/node/ProfileFolloweesListV2',data=postdata,headers=headers).text.encode('utf-8')
        allofthem+=re.findall(r'people\\/[0-9a-zA-Z\-_]{1,}\\',st)

    if int(followee_num)>40:
        for num in range(20,int(followee_num),20):
#            time.sleep(0.5)
            postdata={
                'method':'next',
                'params':'''{"offset":'''+str(num)+''',"order_by":"created","hash_id":"'''+hash_id+'''"}''',
                '_xsrf':_xsrf}

    
            st=session.post(url='http://www.zhihu.com/node/ProfileFolloweesListV2',data=postdata,headers=headers).text.encode('utf-8')
            allofthem+=re.findall(r'people\\/[0-9a-zA-Z\-_]{1,}\\',st)
            len(allofthem)
        postdata={
            'method':'next',
            'params':'''{"offset":'''+str(followee_num)+''',"order_by":"created","hash_id":"'''+hash_id+'''"}''',
            '_xsrf':_xsrf}

    
        st=session.post(url='http://www.zhihu.com/node/ProfileFolloweesListV2',data=postdata,headers=headers).text.encode('utf-8')
        allofthem+=re.findall(r'people\\/[0-9a-zA-Z\-_]{1,}\\',st)
        
        
    allofthem=[i[8:-1] for i in allofthem]
    allofthem+=firstlist
    allofthem = list(set(allofthem))
    allofthem=['http://www.zhihu.com/people/'+i for i in allofthem]
    print '==='
#    time.sleep(0.5)
    return allofthem

################################


def getquestionfollowees(session,url):
    #输入问题地址,返回问题的关注者。忽略了匿名用户。关注数需要大于20。
    #形如：[homepage1,homepage2,......]

    print 'get page'
    url=url+'/followers'
    html=etree.HTML(session.get(url).text.encode('utf-8'))

    _xsrf=html.xpath("/html/body/input[@name='_xsrf']")[0].attrib['value']


    followees=html.xpath("/html/body/div/div/div/div/div/div[@class='zg-gray-normal']/a/strong")[0].text
    followees=int(followees)
    print followees

    req=[]

    first=html.xpath("/html/body/div/div/div/div/div/a[@class='zm-item-link-avatar']")
    first=[i.attrib['href'] for i in first]
    first=['http://www.zhihu.com'+i for i in first]

    
    offset=20
    if followees>=20:
        while True:
        #模拟按键
            print 'button'
            post={'start':'0',
                  'offset':str(offset),
                  '_xsrf':_xsrf}
            time.sleep(0.5)
            req+=[session.post(url,post)]


            offset+=20
            if offset>followees:
                post={'start':'0',
                      'offset':offset,
                      '_xsrf':_xsrf}
                time.sleep(0.5)
                req+=[session.post(url,post)]
                break
    else:
        post={'start':'0',
              'offset':str(followees),
              '_xsrf':_xsrf}
        time.sleep(0.5)
        req+=[session.post(url,post)]




    try:
        req=[i.json()[u'msg'][1].encode('utf-8') for i in req]
    except ValueError,e:
        return req
    
    r=[]
    for reqi in req:
        r+=list(set(re.findall('"/people/[0-9a-zA-Z.\-_]{1,}"',reqi)))

    r=[i[1:-1] for i in r]
    r=['http://www.zhihu.com'+i for i in r]
    first+=r
    first.reverse()
    

    return first


#########################################


def WideAnswer(session,url):
    req=session.get(url).text.encode('utf-8')
    tree=etree.HTML(req)
    name=tree.xpath("/html/body/div/div[@class='zu-main-content']/div[@class='zu-main-content-inner with-indention-votebar']/div/div/div/div/h3[@class='zm-item-answer-author-wrap']/a[@class='zm-item-link-avatar']")
    if name==[]:name='anonymous'
    else:name='http://www.zhihu.com'+name[0].attrib['href']    
    return name

def AnalyseQuestion(session,url):
    #取得答案们的用户主页和答案们的赞同数
    #数据结构：[[homepage1,vote1],[homepage2,vote2],[anonymous,vote3],.......]

    
    headers={
        'Host':'www.zhihu.com',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
#    'Accept':'image/png,image/*;q=0.8,*/*;q=0.5',
#    'Accept-Language':'zh-Hans-CN,zhHans;q=0.5',
#    'Accept-Encoding':'gzip, deflate',
#    'Referer':homepage+'/followees'
#    ,"Cache-Control": "max-age=0",
#    "Connection": "Keep-Alive",
    }
    
    req=session.get(url=url,headers=headers).text.encode('utf-8')
    tree=etree.HTML(req)

    #获取答案数
    num=tree.xpath("/html/body/div/div/div/div/h3[@id='zh-question-answer-num']")[0]
    num=int(num.attrib['data-num'])
    print num

    #获取答案链接及赞同数
    #获取答案链接矩阵
    ans=tree.xpath("/html/body/div/div/div/div/div[@class='zm-item-answer ']")
    ans=[i.attrib['data-atoken'] for i in ans]
    ans=[url+'/answer/'+i for i in ans]
    #获取赞同数
    vote=tree.xpath("/html/body/div/div/div/div/div/div/button/span[@class='count']")
    vote=[int(i.text) for i in vote]
    print len(ans),len(vote)

    #将答案链接变为用户地址
    ans=[WideAnswer(session,i) for i in ans]
    ans_vote=[]
    for i in range(num):
        ans_vote+=[[ans[i],vote[i]]]

    return ans_vote


################################

def Timeline(session,url,pages=10,upvote=True,follow=True,onlyquestion=True):
    #取得时间线上点赞及关注情况
    #返回值格式：[url1,url2,......]
    req=session.get(url).text.encode('utf-8')
    html=etree.HTML(req)
    
    _xsrf=html.xpath("/html/body/input[@name='_xsrf']")[0].attrib['value']

    nodes=html.xpath("/html/body/div/div/div/div/div/div/div[@class='zm-profile-section-item zm-item clearfix']")
    links=html.xpath("/html/body/div/div/div/div/div/div/div[@class='zm-profile-section-item zm-item clearfix']/div/a[@href='%s']"%(url))
    links=[i.getnext() for i in links]
    nodes=[[i.attrib['data-type'],i.attrib['data-time']] for i in nodes]
    links=[i.attrib['href'] for i in links]

    for i in range(len(links)):
        if links[i][0]!='h':
            links[i]='http://www.zhihu.com'+links[i]
    
    infos=[]
    for i in range(len(nodes)):
        infos+=[[nodes[i][0],nodes[i][1],links[i]]]

    start=9999999999
    for i in infos:
        if start>int(i[1]):start=int(i[1])
    for i in range(pages-1):
        time.sleep(0.5)
        post={'start':str(start),
              '_xsrf':_xsrf}
        temp=session.post(url=url+'/activities',data=post)
        temp=temp.json()[u'msg'][1].encode('utf-8')
        if temp=='':break
        temptree=etree.HTML(temp)

        nodeplus=temptree.xpath("//div[@class='zm-profile-section-item zm-item clearfix']")
        linkplus=temptree.xpath("//div[@class='zm-profile-section-item zm-item clearfix']/div/a[@href='%s']"%(url))
        linkplus=[i.getnext() for i in linkplus]

        linkplus=[i.attrib['href'] for i in linkplus]
        nodeplus=[[i.attrib['data-type'],i.attrib['data-time']] for i in nodeplus]

        for i in range(len(linkplus)):
            if linkplus[i][0]!='h':
                linkplus[i]='http://www.zhihu.com'+linkplus[i]

        infoplus=[]
        for i in range(len(nodeplus)):
            infoplus+=[[nodeplus[i][0],nodeplus[i][1],linkplus[i]]]

        start=9999999999
        for i in infoplus:
            if start>int(i[1]):start=int(i[1])
        
        infos+=infoplus

    infos=[[i[0],i[2]] for i in infos]
    
    returnlist=[]
    if onlyquestion==True:
        for i in infos:
            if i[1][21:29]=='question':
                returnlist+=[[i[0],i[1]]]
    else:
        returnlist=infos

    if upvote==False and follow==False:
        return []
    if upvote==True and follow==False:
        miao=[]
        for i in returnlist:
            if i[0]=='a':
                miao+=[i[1]]
        return miao
    if upvote==False and follow==True:
        miao=[]
        for i in returnlist:
            if i[0]!='a':
                miao+=[i[1]]
        return miao
    if upvote==True and follow==True:
        miao=[]
        for i in returnlist:
            miao+=[i[1]]
        return miao


################################################
def setdict(topics):
    '输入大list，返回dict'
    dic={}
    for smalllist in topics:
        for item in smalllist:
            try:
                dic[item]+=1
            except KeyError,e:
                dic.setdefault(item,1)

    try:
        dic.pop('/topic/19776749/organize/entire')
    except KeyError,e:
        pass

    try:
        dic.pop('/topic/19776751/organize/entire')
    except KeyError,e:
        pass
    
    return dic

######################################################
def newgettopics(session,self_num):
#改完了
#    print "分析话题结构"
    topic=[]
#    a=time.time()
    req=session.get('http://www.zhihu.com'+self_num)
#    b=time.time()
    html=etree.HTML(req.text.encode('utf-8'))
        
    #检索信息,查找fathers(2代）
    ftree=html.xpath("//div[@class='zm-topic-tree']")[0]
    chs=ftree.getchildren()
    chs=[etree.tostring(item,encoding='utf-8') for item in chs]


    for i in chs:
            fathers=re.findall('/topic/[0-9]{8}/organize/entire',i)
            real=re.findall('strong',i)
            if len(real)==0 and len(fathers)>1:
                topic+=fathers[-2:-1]
            if len(real)!=0:
                if len(fathers)>2:
                    topic+=fathers[-3:-1]
                if len(fathers)==2:
                    topic+=fathers[-2:-1]
              
            
#    c=time.time()
#    iters2=[i[0] for i in iters if len(i)==3 or len(i)==2]
#    d=time.time()
#    print b-a,c-b,d-c

#    topic=list(set(topic))
#    print "分析完成"
    return topic




def newtopicofsomeone(session,homepage):
    #改完了哦哈哈
    print "获取个人信息"
    '得到topics列表\n结构：[[topic1,topic2,...],[topic3.topic4,...],....]'
    url1=homepage+'/answers?order_by=created&page=1'
    url2=homepage+'/answers?order_by=created&page=2'
    url3=homepage+'/answers?order_by=created&page=3'

#    a=time.time()
    miao=session.get(url1)
#    b=time.time()    
    html0=etree.HTML(miao.text.encode('utf-8'))
    answers0=html0.xpath('/html/body/div/div/div/div/div/div/div/div/div/div/div/textarea')
    answers0=[etree.tostring(i,encoding='utf-8') for i in answers0]
    answers0=[re.findall('/question/[0-9]{8}/answer/[0-9]{8}',i)[0] for i in answers0]

#    c=time.time()
    miao=session.get(url2)
#    d=time.time()
    html1=etree.HTML(miao.text.encode('utf-8'))
    answers1=html1.xpath('/html/body/div/div/div/div/div/div/div/div/div/div/div/textarea')
    answers1=[etree.tostring(i,encoding='utf-8') for i in answers1]
    answers1=[re.findall('/question/[0-9]{8}/answer/[0-9]{8}',i)[0] for i in answers1]

#    e=time.time()
    miao=session.get(url3)
#    f=time.time()
    html2=etree.HTML(miao.text.encode('utf-8'))
    answers2=html2.xpath('/html/body/div/div/div/div/div/div/div/div/div/div/div/textarea')
    answers2=[etree.tostring(i,encoding='utf-8') for i in answers2]
    answers2=[re.findall('/question/[0-9]{8}/answer/[0-9]{8}',i)[0] for i in answers2]

    answers=answers1+answers0+answers2
    #得到答案地址
#    g=time.time()

    total=[]
    for ans in answers:
        html=etree.HTML(session.get('http://www.zhihu.com'+ans).text.encode('utf-8'))
        topics=html.xpath("/html/body/div/div/div/div/div/a[@class='zm-item-tag']")
        topics=[etree.tostring(i,encoding='utf-8') for i in topics]
        topics=[re.findall('/topic/[0-9]{8}',i)[0]+'/organize/entire' for i in topics]
        total.append(topics)
#    h=time.time()
#    print b-a,c-b,d-c,e-d,f-e,g-f,h-g
    print "获取完成"
    return total


def newwidetopics(session,lists):
    '输入topics列表，扩展它'
    topics=[]
    for i in lists:
        topics+=newgettopics(session,i)
        topics.append(i)
    topics=list(set(topics))
    return topics

######################################################

def newgetmatrix(session,homepage):
    print "程序开始"
    a=time.time()
    lists=newtopicofsomeone(session,homepage)
    b=time.time()
    print '扩展话题'
    topics=[newwidetopics(session,item) for item in lists]
    print '扩展完成'
    dic=setdict(topics)
    c=time.time()
    print b-a,c-b
    print "程序结束"
    return dic







