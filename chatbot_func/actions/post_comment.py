import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import configparser
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

# Load env
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

config = configparser.ConfigParser()
config.read('config.ini')
# db connection
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:" \
               f"{os.getenv('POSTGRES_PASSWORD')}@" \
               f"{os.getenv('POSTGRES_HOST')}:" \
               f"{os.getenv('POSTGRES_PORT')}/" \
               f"{os.getenv('POSTGRES_DB')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def add_city(user_tg, city_name, score, comment, connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO cities (user_tg, city_name, score, comment) 
            VALUES (%s, %s, %s, %s);
        """, (user_tg, city_name, score, comment))
        connection.commit()
        logging.info(f"City {city_name} added by user {user_tg} successfully with score {score}.")
    except Exception as e:
        connection.rollback()
        logging.error(f"An error occurred while adding the city: {e}")
    finally:
        cursor.close()


def add_city_command(update: Update, context: CallbackContext) -> None:
    logging.info("add_city_command was called with context args: {}".format(context.args))

    args = context.args
    if len(args) < 4:
        update.message.reply_text(
            "Usage: /addcity <user_name>, <city_name>, <score>, <comment>\n\n"
            "e.g. /addcity your_username, New York, 10, Great place!'\n\n (add '@' in your_username if you wish to be chat with other users)"
        )
        return

    user_tg = args[0]
    city_name = args[1]
    score_str = args[2]
    comment = ' '.join(args[3:])

    try:
        score = int(score_str)
    except ValueError:
        update.message.reply_text("Score must be an integer.")
        return

    connection = context.bot_data.get('db_connection')
    if connection is None:
        logging.error("Database connection not initialized.")
        update.message.reply_text("Database connection not initialized.")
        return

    try:
        add_city(user_tg, city_name, score, comment, connection)
        update.message.reply_text(f"City {city_name} added successfully with score {score}.")
    except Exception as e:
        logging.error(f"An error occurred while adding the city: {e}")
        update.message.reply_text("An error occurred while adding the city.")