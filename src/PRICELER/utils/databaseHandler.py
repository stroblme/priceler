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
		c.execute('''CREATE TABLE userRequests(userId text, url text, dateUpdated text, cheapestPrice real, latestPrice real)''')
		conn.commit()
		print("New Table created")
	except:
		print("Using existing table")
		
	return result

def requestPrice(url):
    price=reqH.getPrice(url)
    if(price==-1):
        raise ValueError('Running Request failed due to invalid value')
    else:
        return float(price)

def dictToArray(dict):
    array=[dict['userId'],dict['url'],dict['dateUpdated'],dict['cheapestPrice'],dict['latestPrice']]
    return array

def arrayToDict(array):
    dict={'userId':array[0],'url':array[1],'dateUpdated':array[2],'cheapestPrice':array[3],'latestPrice':array[4]}
    return array


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
            userRequest['latestPrice']=requestPrice(userRequest['url'])
            userRequest['cheapestPrice']=userRequest['latestPrice'] #when adding, there is no cheaper price
            userRequest['dateUpdated']=str(datetime.now().date())
            c.execute('INSERT INTO userRequests VALUES (?,?,?,?,?)',dictToArray(userRequest))
            print("User Request added:\n"+str(userRequest))
        except ValueError:
            print("adding request has been cancelled due to bad value")
        except Exception as e:
            print("databaseHandler has caused an error when adding request:\n\t"+str(e))
            result=-1
    elif(operation=='del'):
        c=conn.cursor()
        try:
            userUrl=[userRequest['userId'],userRequest['url']]
            c.execute('DELETE userRequests WHERE userId=? AND url=?',userUrl)
            print("User Request deleted:\n"+str(userRequest))
        except Exception as e:
            print("databaseHandler has caused an error when deleting request:\n\t"+str(e))
            result=-1
    elif(operation=='update'):
        c=conn.cursor()
        try:
            userRequest['latestPrice']=requestPrice(userRequest['url'])
            if(userRequest['latestPrice']<userRequest['cheapestPrice']):	#update cheapes price if  latest one is lower
                userRequest['cheapestPrice']=userRequest['latestPrice'] #latest price is cheapest one
                userRequest['dateUpdated']=str(datetime.now().date())
                data={'state':'updated','userRequest':userRequest}
                c.execute('UPDATE userRequests SET cheapestPrice=? WHERE userId=? AND url=?',(userRequest['cheapestPrice'],userRequest['userId'],userRequest['url']))

            #c.execute('UPDATE userRequests SET (?,?,?,?,?)',dictToArray(userRequest))
            c.execute('UPDATE userRequests SET latestPrice=? WHERE userId=? AND url=?',(userRequest['latestPrice'],userRequest['userId'],userRequest['url']))
            data={'state':'nochange','userRequest':userRequest}
            print("User Request updated:\n"+str(userRequest))
        except ValueError:
            print("adding request has been cancelled due to bad value")
            result=-1
        except Exception as e:
            print("databaseHandler has caused an error when updating request:\n\t"+str(e))
            result=-1
    elif(operation=='get'):
        c=conn.cursor()
        data=[]
        try:
            uid = (userRequest['userId'],)
            for row in c.execute('SELECT * FROM userRequests WHERE userId=? ORDER BY dateUpdated'):
                data.append(row)
            print("User Request returned:\n"+str(userRequest))
        except Exception as e:
            print("databaseHandler has caused an error when getting request:\n\t"+str(e))
            result=-1

    conn.commit()
    conn.close()

    LOCK=0
    return {'result':result,'data':data}