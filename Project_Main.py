from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import configparser
import logging
import redis
from Project_ChatGPT import HKBU_ChatGPT


# Set global variables
global redis_project
target_cities = ['Tokyo', 'Bangkok', 'Paris']
chosen_city = ''
user_id = ''
username = ''


def main():
    # To load tokens
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    global redis_project
    redis_project = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']), port=int(config['REDIS']['REDISPORT']))
    
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)


    # Set logging module
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    

    # Set dispatchers
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), unknown_input))
    dispatcher.add_handler(CommandHandler("start", get_start))
    dispatcher.add_handler(CommandHandler("start_over", start_over))    
    dispatcher.add_handler(CommandHandler("add", add_review))
    dispatcher.add_handler(CallbackQueryHandler(chosen_option))

    
    # To start the bot:
    updater.start_polling()
    updater.idle()
    



########################################################################################################
    # To build commands
########################################################################################################

def unknown_input(update, context):
    update.message.reply_text('Sorry, I am not following you.')
    get_start(update, context)


def start_over(update, context):
    get_start(update, context)


def get_start(update, context):
    keyboard = [
        [
            InlineKeyboardButton("📄 Read reviews", callback_data="read_review"),
        ],
        [
            InlineKeyboardButton("📝 Write a review", callback_data="write_review"),
        ],
        [
            InlineKeyboardButton("✈ Plan a trip", callback_data="plan_trip"),
        ]
    ]
    reply_initial_choice = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="This is a travel planner bot. What are you looking for?", reply_markup=reply_initial_choice)


def add_review(update, context):
    review = ' '.join(context.args[:])

    global redis_project

    redis_project.incr(chosen_city)
    chosen_city_count = redis_project.get(chosen_city).decode('UTF-8')
    chosen_city_key = chosen_city + '_' + chosen_city_count

    redis_project.set(chosen_city_key, review)



########################################################################################################
    # To deal with action after all possible options 
########################################################################################################

def chosen_option(update, context):
    query = update.callback_query
    option = query.data

    global chosen_city, user_id, username
    global redis_project


    ####################################################################################################
        # For choosing "Read reviews"
    ####################################################################################################

    if option == "read_review":
        keys = []
        cursor = '0'
        while cursor != 0:
            cursor, partial_keys = redis_project.scan(cursor=cursor)
            keys.extend(partial_keys)

        # Iterate over the keys and print the key-value pairs
        for key in keys:
            for city in target_cities:
                if key.decode().startswith(city):
                    value = redis_project.get(key)
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{city}: {value.decode()}")




    ####################################################################################################
        # For choosing "Write a review"
    ####################################################################################################
                
    elif option == "write_review":
        keyboard = [
            [
                InlineKeyboardButton("Tokyo", callback_data="Tokyo_review"),
                InlineKeyboardButton("Bangkok", callback_data="Bangkok_review"),
                InlineKeyboardButton("Paris", callback_data="Paris_review"),
            ]
        ]
        reply_write_review = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=query.message.chat_id, text="Which city caught your eye for a review?", reply_markup=reply_write_review)


    elif option == "Tokyo_review":
        user = query.from_user
        user_id = user.id
        username = user.username
        
        chosen_city = option.split('_')[0]
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Please write your review starting with /add {chosen_city}')
    

    elif option == "Bangkok_review":
        user = query.from_user
        user_id = user.id
        username = user.username
        
        chosen_city = option.split('_')[0]
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Please write your review starting with /add {chosen_city}')

    
    elif option == "Paris_review":
        user = query.from_user
        user_id = user.id
        username = user.username
        
        chosen_city = option.split('_')[0]
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Please write your review starting with /add {chosen_city}')




########################################################################################################
    # To start the bot
########################################################################################################

if __name__ == '__main__':
    main()


