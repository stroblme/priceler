#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from lxml import html

ELEMENTIDS=[['amazon','priceblock_ourprice']]

#--------------------------------------------------------------------------------------------
# Extracts value at element id from given tree
#--------------------------------------------------------------------------------------------
def getValueFromTree(tree, elementId):
    result=0
    try:
        price=tree.xpath('//span[@id="'+elementId+'"]/text()')
        price=price[0].split( )
        price=price[1].split(',')
        result=price[0]
    except:
        print("Request Handler has caused an error when parsing Tree")
        result=-1
    return result

#--------------------------------------------------------------------------------------------
# extracts element id from specific webpage using look up tables
#--------------------------------------------------------------------------------------------
def urlParser(url):
    #TODO: Only for amazon yet
    elementId=ELEMENTIDS[0][1]
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