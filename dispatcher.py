from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def start(update, context):
    import random
    bot_username = random.choice(['@groupz7940_1_bot', '@groupz7940_2_bot'])
    update.message.reply_text(f"Hi! Please talk to {bot_username} for assistance.")
    
def handle_message(update, context):
    text = update.message.text.lower()
    if text == "hi":

        update.message.reply_text("Hello! Welcome to GroupZ chatbot dispatcher type /start to start")

def main():
    load_dotenv()
    dispatcher_bot_token = os.getenv('TELEGRAM_DISPATCHER_ACCESS_TOKEN')
    if not dispatcher_bot_token:
        logging.error('The dispatcher bot token is not set. Please check your .env file.')
        return
    updater = Updater(token=dispatcher_bot_token, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))

    updater.start_polling()
    updater.idle()