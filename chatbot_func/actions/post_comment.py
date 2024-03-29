from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import City,Base
import configparser
import psycopg2
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

config = configparser.ConfigParser()
config.read('config.ini')
# db connection
DATABASE_URL = f"postgresql://{config['POSTGRESQL']['USER']}:" \
               f"{config['POSTGRESQL']['PASSWORD']}@" \
               f"{config['POSTGRESQL']['HOST']}:" \
               f"{config['POSTGRESQL']['PORT']}/" \
               f"{config['POSTGRESQL']['DBNAME']}"

def init_database(context: CallbackContext) -> None:
    connection = psycopg2.connect(DATABASE_URL)
    context.bot_data['db_connection'] = connection
    logging.info("Database connection initialized and stored in context.")


def add_city(city_name, score, comment, connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO cities (city_name, score, comment) 
            VALUES (%s, %s, %s);
        """, (city_name, score, comment))
        connection.commit()
        logging.info(f"City {city_name} added successfully with score {score}.")
    except Exception as e:
        connection.rollback()
        logging.error(f"An error occurred while adding the city: {e}")
    finally:
        cursor.close()


def add_city_command(update: Update, context: CallbackContext) -> None:
    
    logging.info("add_city_command was called with context args: {}".format(context.args))
    args = context.args
    if len(args) < 3:
        update.message.reply_text("Usage: /addcity <name> <score> <comment>")
        return

    city_name, score_str, *comment_parts = args
    comment = ' '.join(comment_parts)

    # Try to convert the score to an integer
    try:
        score = int(score_str)
    except ValueError:
        update.message.reply_text("Score must be an integer.")
        return

    # Retrieve the database connection
    connection = context.bot_data.get('db_connection')
    if connection is None:
        logging.error("Database connection not initialized.")
        update.message.reply_text("Database connection not initialized.")
        return

    #  add to the database
    try:
        add_city(city_name, score, comment, connection)
        update.message.reply_text(f"City {city_name} added successfully with score {score}.")
    except Exception as e:
        logging.error(f"An error occurred while adding the city: {e}")
        update.message.reply_text(f"An error occurred while adding the city.")