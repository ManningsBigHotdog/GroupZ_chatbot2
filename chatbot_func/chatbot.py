import os
import configparser
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import psycopg2

from chatbot_func.actions.post_comment import add_city_command


def main():
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    chatbot_env = os.getenv('CHATBOT_ENV', 'TELEGRAM')
    updater = Updater(token=config[chatbot_env]['ACCESS_TOKEN'], use_context=True)
    dispatcher = updater.dispatcher
    chatgpt = HKBU_ChatGPT(config)
    updater.dispatcher.bot_data['chatgpt'] = chatgpt

    # Connect to db
    init_database(dispatcher.bot_data)

    #handlers
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler("search", get_comments))
    dispatcher.add_handler(CommandHandler('addcity', add_city_command))

    # Start the bot
    updater.start_polling()
    updater.idle()

    # Close the database connection
    if 'db_connection' in dispatcher.bot_data:
        dispatcher.bot_data['db_connection'].close()

if __name__ == '__main__':
    main()