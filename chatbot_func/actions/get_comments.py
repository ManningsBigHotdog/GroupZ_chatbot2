import logging
import os
import configparser
import psycopg2
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

def init_database(bot_data: dict) -> None:
    config = configparser.ConfigParser()
    config.read('config.ini')
    # Connection to database
    connection = psycopg2.connect(
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'],
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT']
    )
    bot_data['db_connection'] = connection
    logging.info("Database connection initialized and stored in context.")

def build_menu(buttons, n_cols):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return menu

def get_comments(update: Update, context: CallbackContext, offset=0, show_all=False) -> None:
    message = None
    limit = 5  # record to show for first search
    try:
        # callback queries
        if update.callback_query:
            message = update.callback_query.message
            query_data = update.callback_query.data.split(':')
            command, city_name = query_data[0], query_data[1]
            if command == "show_more_comments":
                offset = int(query_data[2])
            elif command == "show_all_comments":
                show_all = True
            update.callback_query.answer()

        # regular messages
        else:
            message = update.message
            city_name = context.args[0] if context.args else None
            if not city_name:
                message.reply_text("Usage: /search <City> e.g. /search Tokyo")
                return

        # Database connection check
        connection = context.bot_data.get('db_connection')
        if connection is None:
            message.reply_text("Database connection not initialized.")
            logging.error("Database connection not initialized.")
            return

        cursor = connection.cursor()

        # cal average score
        cursor.execute("SELECT AVG(score) FROM cities WHERE city_name = %s;", (city_name,))
        avg_score = cursor.fetchone()[0]
        avg_score_text = f"Average score for {city_name}: {avg_score:.2f}\n" if avg_score else "No scores yet.\n"

        # select comments
        if show_all:
            cursor.execute("SELECT comment FROM cities WHERE city_name = %s ORDER BY created_at DESC;", (city_name,))
        else:
            cursor.execute("SELECT comment FROM cities WHERE city_name = %s ORDER BY created_at DESC LIMIT %s OFFSET %s;", (city_name, limit, offset * limit))
        comments = cursor.fetchall()

        # Cal total comments
        cursor.execute("SELECT COUNT(*) FROM cities WHERE city_name = %s;", (city_name,))
        total_comments = cursor.fetchone()[0]

        has_more_comments = (offset + 1) * limit < total_comments if not show_all else False
        comments_list = [f"{idx + offset * limit + 1}. {comment[0]}" for idx, comment in enumerate(comments)]

        # reply message
        message_text = f"{avg_score_text}Comments for {city_name}:\n\n" + "\n".join(comments_list) if comments else "No comments to display."

        # Create button list
        button_list = []
        if not show_all:
            if offset > 0:
                button_list.append(InlineKeyboardButton("Show previous", callback_data=f"show_more_comments:{city_name}:{offset-1}"))
            if has_more_comments:
                button_list.append(InlineKeyboardButton("Show more", callback_data=f"show_more_comments:{city_name}:{offset+1}"))
            button_list.append(InlineKeyboardButton("Show all", callback_data=f"show_all_comments:{city_name}"))
        reply_markup = InlineKeyboardMarkup([[button] for button in button_list]) if button_list else None

        # Send message with inline keyboard
        message.reply_text(message_text, reply_markup=reply_markup)

    except Exception as e:
        logging.error(f"Error while getting comments: {e}")
        if message:
            message.reply_text("An error occurred while fetching comments.")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    callback_data = query.data.split(':')
    action = callback_data[0]

    if action == 'show_more_comments':
        city_name = callback_data[1]
        offset = int(callback_data[2])
        context.args = [city_name, str(offset + 5)]
        get_comments(update, context)
    elif action == 'show_all_comments':
        city_name = callback_data[1]
        context.args = [city_name, 'show_all']
        get_comments(update, context)
    else:
        query.edit_message_text(text="You clicked a button, but it has no associated action.")