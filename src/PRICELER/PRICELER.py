
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, getopt

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import logging

from utils import databaseHandler as dbH


POLLING=60*30	#every 30 minutes


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#--------------------------------------------------------------------------------------------
# Triggers the Request handler, when executed
#--------------------------------------------------------------------------------------------
def requestPoll(bot, job):
    userRequest={'userId':job.context}
    getRes=dbH.runOperation('get',userRequest)       #get a list of the urls of the current user

    for getResList in getRes['data']:                              #iterate through the users url to check if update needed
        try:
            updateRes=dbH.runOperation('update',getResList)
            if(updateRes['result']==-1):
                print("Error occured when updating Request")
                break
            url=updateRes['data']['userRequest']['url'] #Get url from returned data
            latestPrice=updateRes['data']['userRequest']['latestPrice'] #Get latest price from returned data

            if(updateRes['data']['state']=='updated'):          #prints out notification when price is sunc
                bot.send_message(job.context, text='Item '+url+' has been updated from '+str(getResList[3])+' to '+str(latestPrice))
            #else:
            #    bot.send_message(job.context, text='Item '+url+' has not been updated from '+str(getResList[3])+' to '+str(latestPrice))
        except:
            print("update Request cancelled")
#--------------------------------------------------------------------------------------------
# Starts a Timer thread and adds it to the queue
#--------------------------------------------------------------------------------------------
def set_timer(bot, update, job_queue, chat_data):
	update.message.reply_text('Priceler\nIn Development! Data may get lost! See /help for further information')
	
	chat_id = update.message.chat_id

	# Add job to queue
	job = job_queue.run_repeating(requestPoll, POLLING, first=None, context=chat_id, name=None)
	chat_data['job'] = job

	update.message.reply_text('Polling succesfully started')

#--------------------------------------------------------------------------------------------
# adds an Request to the database
#--------------------------------------------------------------------------------------------
def addRequest(bot, update, args, chat_data):
    chat_id = update.message.chat_id
    try:
        userRequest={'userId':chat_id,'url':str(args[0])}
        
        if(dbH.runOperation('add',userRequest) == -1):
            update.message.reply_text('Error occurred when adding Request')
        else:
            update.message.reply_text('Request successfully accepted')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <url>')

#--------------------------------------------------------------------------------------------
# deletes a Request from the database
#--------------------------------------------------------------------------------------------
def delRequest(bot, update, args, chat_data):
    chat_id = update.message.chat_id
    try:
        userRequest={'userId':chat_id,'url':str(args[0])}
        dbH.runOperation('del',userRequest)
        update.message.reply_text('Request successfully deleted!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /del <url>')

#--------------------------------------------------------------------------------------------
# show list of all Requests in stored for current user
#--------------------------------------------------------------------------------------------	
def showRequests(bot, update, chat_data):
    chat_id = update.message.chat_id
    try:
        userRequest={'userId':chat_id}
        getRes=dbH.runOperation('get',userRequest)       #get a list of the urls of the current user
        output="UserId:\t"+str(chat_id)+"\nUpdating items.. This may take some time..\n"
        update.message.reply_text(output)
        output=""
        for getResList in getRes['data']:                              #iterate through the users url to check if update needed
            updateRes=dbH.runOperation('update',getResList)
            if(updateRes['result']==-1):
                pass
            else:
                title=updateRes['data']['userRequest']['title']
                output=output+str(title)+"\n\n"
                url=updateRes['data']['userRequest']['url']
                output=output+"\tURL:\t"+str(url)+"\n"
                dateAdded=updateRes['data']['userRequest']['dateAdded']
                output=output+"\tDate Addded:\t"+str(dateAdded)+"\n"
                latestPrice=updateRes['data']['userRequest']['latestPrice']
                output=output+"\tLatest Price:\t"+str(latestPrice)+"\n"
                cheapestPrice=updateRes['data']['userRequest']['cheapestPrice']
                output=output+"\tCheapest Price:\t"+str(cheapestPrice)+"\n"

                update.message.reply_text(output)
                output=""
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /show <url>')

#--------------------------------------------------------------------------------------------
# stops the Timer, i.e. the user has quitted
#--------------------------------------------------------------------------------------------
def stopTimer(bot, update, args, chat_data):
	if 'job' not in chat_data:
		update.message.reply_text('You have no active requests')
		return

	job = chat_data['job']
	job.schedule_removal()
	del chat_data['job']

	chat_id = update.message.chat_id

#--------------------------------------------------------------------------------------------
# displays the help
#--------------------------------------------------------------------------------------------
def help(bot, update):
    helpText="Priceler helps you to get the best price on amazon\n"
    helpText=helpText+"\t/add URL\tInput the url to the item priceler should track\n"
    helpText=helpText+"\t/del URL\tNo need to keep track? Delete unnecessary urls!\n"
    helpText=helpText+"\t/show\tShows all your added urls\n"
    helpText=helpText+"\t/start\tStart the notification service to get informed when the price has dropped"
    update.message.reply_text(helpText)
    # TODO: Implement



#--------------------------------------------------------------------------------------------
# Closes Database, when bot is stopping or caused an error
#--------------------------------------------------------------------------------------------
def error(bot, update, error):
	global conn
	"""Log Errors caused by Updates."""
	LOCK=0
	dbH.runOperation('close',None)
	logger.warning('Update "%s" caused error "%s"', update, error)

#--------------------------------------------------------------------------------------------
# Main entry point
#--------------------------------------------------------------------------------------------
def main(argv):
    apiToken=""
    try:
        opts, args = getopt.getopt(argv,"t:",["apiToken="])
    except getopt.GetoptError:
        print("PRICELER.py -t <apiToken>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("PRICELER.py -t <apiToken>")
            sys.exit()
        elif opt in ("-t", "--apiToken"):
            apiToken=str(arg)

    if(apiToken==""):
        print("No API Token provided")
        sys.exit()

    """Start the bot."""
    dbH.runOperation('open', None)

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(apiToken)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    # dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("start", 
								    set_timer,
								    pass_job_queue=1,
								    pass_chat_data=1))
    dp.add_handler(CommandHandler("add", 
                                    addRequest, 
								    pass_args=1, 
								    pass_chat_data=1))
    dp.add_handler(CommandHandler("del", 
								    delRequest, 
                                    pass_args=1, 
								    pass_chat_data=1))
    dp.add_handler(CommandHandler("show", 
								    showRequests, 
								    pass_chat_data=1))
    dp.add_handler(CommandHandler("stop", 
								    stopTimer, 
								    pass_chat_data=1))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram


    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main(sys.argv[1:])