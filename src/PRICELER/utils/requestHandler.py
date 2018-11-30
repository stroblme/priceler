#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from lxml import html

ELEMENTIDS={'amazon':['productTitle','priceblock_ourprice','priceblock_dealprice']}

#--------------------------------------------------------------------------------------------
# Extracts value at element id from given tree
#--------------------------------------------------------------------------------------------
def getValueFromTree(tree, elementId):
    result=0
    try:
        price=float(0)
        title=""
        for eId in elementId:
            if('price' in eId):
                try:
                    tPrice=tree.xpath('//span[@id="'+eId+'"]/text()')
                    tPrice=tPrice[0].split( )
                    tPrice=tPrice[1].split(',')
                    print(tPrice)
                    tPrice=float(tPrice[0])
                    if(price==0 or tPrice<price):
                        price=tPrice
                except:
                    pass
            elif('product' in eId):
                try:
                    title=tree.xpath('//span[@id="'+eId+'"]/text()')
                    title=str(title[0]).replace('\n','')
                    title=title.replace('    ','')  #There shouldn't be laarge spaces
                except:
                    pass
        
        data={'price':price,'title':title}
        if(price==0):
            result=-1
    except:
        print("Request Handler has caused an error when parsing Tree")
        result=-1
    return {'result':result,'data':data}

#--------------------------------------------------------------------------------------------
# extracts element id from specific webpage using look up tables
#--------------------------------------------------------------------------------------------
def urlParser(url):
    #TODO: Only for amazon yet
    if('amazon' in url):
        elementId=ELEMENTIDS['amazon']  #get eids from lut
        url=url.split('/ref=',1)[0]     #Delete unnecessary personalization from url

    return {'eId':elementId,'url':url}

#--------------------------------------------------------------------------------------------
# Sends a request to the given page and outputs the value of the element id
#--------------------------------------------------------------------------------------------
def getPrice(url):
    data=0
    result=0
    try:
        urlRes=urlParser(url)
        r=requests.get(urlRes['url'])
        tree=html.fromstring(r.content)
        
        value=getValueFromTree(tree, urlRes['eId'])
        if(value['result']==-1):
            raise ValueError('Running Request failed due to invalid value in Request Handler')
        
        data=value['data']
        result=1
    except:
        print("Request Handler has caused an error"+str(e))
        result=-1
    return {'result':result,'data':data}