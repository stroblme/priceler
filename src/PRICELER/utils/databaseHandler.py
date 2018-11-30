#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

from utils import requestHandler as reqH

DATABASEPATH="requests.db"
LOCK=0

def createTable(conn):
	result=0
	c = conn.cursor()
	try:
		c.execute('''CREATE TABLE userRequests(userId text, title text, url text, dateAdded text, cheapestPrice real, latestPrice real)''')
		conn.commit()
		print("New Table created")
	except:
		print("Using existing table")
		
	return result

def requestData(url):
    requestRes=reqH.getPrice(url)
    if(requestRes['result']==-1):
        raise ValueError('Running Request failed due to invalid value')
    else:
        return requestRes['data']

def shortenURL(url):
    url=reqH.urlParser(url)['url']
    return url

def dictToArray(dict):
    array=[dict['userId'],dict['title'],dict['url'],dict['dateAdded'],dict['cheapestPrice'],dict['latestPrice']]
    return array

def arrayToDict(array):
    dict={'userId':array[0],'title':array[1],'url':array[2],'dateAdded':array[3],'cheapestPrice':array[4],'latestPrice':array[5]}
    return dict


def runOperation(operation, userRequest):
    global LOCK
    result = 0
    data = None

    if LOCK:
        print("Database currently locked.. waiting")
        while(LOCK):
            pass
        print("...unlocked")
   
    #Enable Lock and load database
    LOCK=1
    conn = sqlite3.connect('data/requests.db')

    if(operation=='close'):
        print("Closing Database")
    elif(operation=='open'):
        result=createTable(conn)
    elif(operation=='add'):
        c=conn.cursor()
        try:
            userRequest['url']=shortenURL(userRequest['url'])
            requestRes=requestData(userRequest['url'])
            userRequest['latestPrice']=float(requestRes['price']) 
            userRequest['title']=str(requestRes['title'])
            userRequest['cheapestPrice']=userRequest['latestPrice'] #when adding, there is no cheaper price
            userRequest['dateAdded']=str(datetime.now().date())
            c.execute('INSERT INTO userRequests VALUES (?,?,?,?,?,?)',dictToArray(userRequest))
            print("User Request added:\n"+str(userRequest))
        except ValueError:
            print("adding request has been cancelled due to bad value")
            result = -1
        except Exception as e:
            print("databaseHandler has caused an error when adding request:\n\t"+str(e))
            result=-1
    elif(operation=='del'):
        c=conn.cursor()
        try:
            userRequest['url']=shortenURL(userRequest['url'])
            c.execute('DELETE FROM userRequests WHERE userId=? AND url=?',(userRequest['userId'],userRequest['url']))
            print("User Request deleted:\n"+str(userRequest))
        except Exception as e:
            print("databaseHandler has caused an error when deleting request:\n\t"+str(e))
            result=-1
    elif(operation=='update'):
        c=conn.cursor()
        try:
            requestRes=requestData(userRequest['url'])
            userRequest['latestPrice']=float(requestRes['price']) 

            if(userRequest['latestPrice']<userRequest['cheapestPrice']):	#update cheapes price if  latest one is lower
                userRequest['cheapestPrice']=userRequest['latestPrice'] #latest price is cheapest one
                userRequest['dateAdded']=str(datetime.now().date())
                data={'state':'updated','userRequest':userRequest}  #set "updated" flag
                c.execute('UPDATE userRequests SET cheapestPrice=? WHERE userId=? AND url=?',(userRequest['cheapestPrice'],userRequest['userId'],userRequest['url']))
            else:
                #c.execute('UPDATE userRequests SET (?,?,?,?,?)',dictToArray(userRequest))
                c.execute('UPDATE userRequests SET latestPrice=? WHERE userId=? AND url=?',(userRequest['latestPrice'],userRequest['userId'],userRequest['url']))
                data={'state':'nochange','userRequest':userRequest}
                print("User Request updated:\n"+str(userRequest))
        except ValueError:
            print("updating request has been cancelled due to bad value")
            result=-1
        except Exception as e:
            print("databaseHandler has caused an error when updating request:\n\t"+str(e))
            result=-1
    elif(operation=='get'):
        c=conn.cursor()
        data=[]
        try:
            uid = (userRequest['userId'],)
            for row in c.execute('SELECT * FROM userRequests WHERE userId=? ORDER BY dateAdded', uid):
                data.append(arrayToDict(row))
            print("User Request returned:\n"+str(userRequest))
        except Exception as e:
            print("databaseHandler has caused an error when getting request:\n\t"+str(e))
            result=-1

    conn.commit()
    conn.close()

    LOCK=0
    return {'result':result,'data':data}