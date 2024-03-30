import os
from dotenv import load_dotenv
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from chatbot_func.actions.chatgpt_func import ChatGPT, equiped_chatgpt
from chatbot_func.actions.get_comments import get_comments, init_database, handle_navigation
from chatbot_func.actions.post_comment import add_city_command
from chatbot_func.actions.plan_trip import plan_trip
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
                "- /plantrip - Help you to plan a trip of the city your want to go\n"
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
    chatgpt = ChatGPT()
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
    dispatcher.add_handler(CommandHandler("plantrip", plan_trip))
    
    # Start the bot
    updater.start_polling()
    updater.idle()

    if 'db_connection' in dispatcher.bot_data:
        dispatcher.bot_data['db_connection'].close()

if __name__ == '__main__':
    main()