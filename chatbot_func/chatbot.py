import os
<<<<<<< HEAD
import configparser
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import psycopg2
from chatbot_func.actions.chatgpt_func import HKBU_ChatGPT, equiped_chatgpt
from chatbot_func.actions.get_comments import get_comments, button, init_database
from chatbot_func.actions.post_comment import add_city_command

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    button_data = query.data
    if button_data == 'show_functions':
        functions_text = """
        Here are the functions you can use:
        /start - Start the bot and show this message.
        /search - Search for comments.
        /addcity - Add a new city comment.
        """
        context.bot.send_message(chat_id=query.message.chat_id, text=functions_text)

keyboard = [[InlineKeyboardButton("Show Functions", callback_data='show_functions')]]
reply_markup = InlineKeyboardMarkup(keyboard)

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Hello! Use the button below to trigger a function.', reply_markup=reply_markup)

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
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler("search", get_comments))
    dispatcher.add_handler(CommandHandler('addcity', add_city_command))
    
   
=======
from dotenv import load_dotenv
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from chatbot_func.actions.chatgpt_func import HKBU_ChatGPT, equiped_chatgpt, plan_trip
from chatbot_func.actions.get_comments import get_comments, init_database, handle_navigation
from chatbot_func.actions.post_comment import add_city_command

#load env file
load_dotenv()

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    logging.info("Button callback query received: %s", query.data)
    try:
        query.answer()
        button_data = query.data
        if button_data == 'show_functions':
            functions_text = (
                "Here are the functions you can use:\n"
                "- /start - Start the bot and show this message.\n"
                "- /search - Search for comments.\n"
                "- /addcity - Add a new city comment.\n"
                "- /plan_trip- Add your desired city.\n"
                "- Normal sending message - ChatGPT function"
            )
            query.edit_message_text(text=functions_text)
    except Exception as e:
        logging.exception("Error in button function: %s", e)
        query.edit_message_text(text="An error occurred while processing your request.")

def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Show Functions", callback_data='show_functions')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Hello! Please click this button to see what this chatbot can do.', reply_markup=reply_markup)

def main():
    bot_type = os.getenv('BOT_TYPE')
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    
    if bot_type == 'CHATBOT1':
        access_token = os.getenv('TELEGRAM_BOT_1_ACCESS_TOKEN')
    elif bot_type == 'CHATBOT2':
        access_token = os.getenv('TELEGRAM_BOT_2_ACCESS_TOKEN')
    else:
        logging.error("BOT_TYPE environment variable is not set correctly. It must be either 'CHATBOT1' or 'CHATBOT2'.")
        return

    if not access_token:
        logging.error(f"Access token for {bot_type} is not set. Please check your .env file.")
        return
    updater = Updater(token=access_token, use_context=True)
    dispatcher = updater.dispatcher
    chatgpt = HKBU_ChatGPT()
    updater.dispatcher.bot_data['chatgpt'] = chatgpt
    # Connect to db
    init_database(dispatcher.bot_data)

    # Handlers
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button, pattern='^show_functions$'))
    dispatcher.add_handler(CommandHandler("search", get_comments))
    dispatcher.add_handler(CommandHandler('addcity', add_city_command))
    dispatcher.add_handler(CallbackQueryHandler(handle_navigation, pattern='^navigate_comments:'))
    dispatcher.add_handler(CommandHandler("plan_trip", plan_trip))
    
>>>>>>> origin/simon-push
    # Start the bot
    updater.start_polling()
    updater.idle()

<<<<<<< HEAD
    # Close the database connection
=======
>>>>>>> origin/simon-push
    if 'db_connection' in dispatcher.bot_data:
        dispatcher.bot_data['db_connection'].close()

if __name__ == '__main__':
    main()