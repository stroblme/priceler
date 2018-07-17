#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from lxml import html

ELEMENTIDS={'amazon':['priceblock_ourprice','priceblock_dealprice']}

#--------------------------------------------------------------------------------------------
# Extracts value at element id from given tree
#--------------------------------------------------------------------------------------------
def getValueFromTree(tree, elementId):
    result=0
    try:
        price=0
        for eId in elementId:
            print(eId)
            try:
                tPrice=tree.xpath('//span[@id="'+eId+'"]/text()')
                tPrice=tPrice[0].split( )
                tPrice=tPrice[1].split(',')
                tPrice=int(tPrice[0])
                print(tPrice)
                print(price)
                if(price==0 or tPrice<price):
                    price=tPrice
            except:
                pass
        
        result=price
        print("res"+str(price))
    except:
        print("Request Handler has caused an error when parsing Tree")
        result=-1
    return result

#--------------------------------------------------------------------------------------------
# extracts element id from specific webpage using look up tables
#--------------------------------------------------------------------------------------------
def urlParser(url):
    #TODO: Only for amazon yet
    elementId=ELEMENTIDS['amazon']
    return elementId

#--------------------------------------------------------------------------------------------
# Sends a request to the given page and outputs the value of the element id
#--------------------------------------------------------------------------------------------
def getPrice(url):
    result = 0
    try:
        r=requests.get(url)
        tree=html.fromstring(r.content)
        eId=urlParser(url)
        price=getValueFromTree(tree, eId)
        result=price
    except:
        print("Request Handler has caused an error"+str(e))
        result=-1
    return result