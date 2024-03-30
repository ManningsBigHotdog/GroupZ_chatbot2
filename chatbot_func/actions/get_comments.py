import logging
import os
from dotenv import load_dotenv
import psycopg2
from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, Updater

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def init_database(bot_data: dict) -> None:
    try:
        connection = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT')
        )
        bot_data['db_connection'] = connection
        logging.info("Database connection initialized and stored in context.")
    except psycopg2.Error as e:
        logging.error("Unable to connect to the database: %s", e)
        bot_data['db_connection'] = None

COMMENTS_PER_PAGE = 5

def get_comments(update: Update, context: CallbackContext) -> None:
    message = update.effective_message
    city_name = None
    page = 0
    if update.callback_query:
        query = update.callback_query
        query.answer()
        callback_data = query.data.split(':')
        _, city_name, page = callback_data
        page = int(page)
        message = query.message
    elif context.args:
        city_name = " ".join(context.args)
    if not city_name:
        message.reply_text("Usage: /search <City> e.g. /search Tokyo")
        return
    connection = context.bot_data.get('db_connection')
    if not connection:
        message.reply_text("Database connection is not available.")
        return
    
    with connection.cursor() as cursor:
        offset = page * COMMENTS_PER_PAGE
        cursor.execute(
            """
            SELECT comment, user_tg FROM public.cities WHERE city_name = %s
            ORDER BY created_at DESC LIMIT %s OFFSET %s;
            """,
            (city_name, COMMENTS_PER_PAGE, offset)
        )
        comments = cursor.fetchall()

        if not comments and page == 0:
            message.reply_text(f"No comments found for {city_name}.")
            return
        elif not comments:
            message.reply_text("No more comments.")
            return
        cursor.execute("SELECT AVG(score) FROM public.cities WHERE city_name = %s;", (city_name,))
        avg_score = cursor.fetchone()[0]
        avg_score_text = f"Average score for {city_name}: {avg_score:.2f}\n" if avg_score else "No scores yet.\n"
    comments_text = "\n".join([f"{idx + 1 + offset}. {comment[0]} (User: {comment[1] or 'Unknown'})" for idx, comment in enumerate(comments)])
    message_text = f"{avg_score_text}Comments for {city_name}:\n\n{comments_text}"

   
    button_list = []
    if page > 0:
        button_list.append(InlineKeyboardButton("Previous", callback_data=f"navigate_comments:{city_name}:{page-1}"))
    if len(comments) == COMMENTS_PER_PAGE:
        button_list.append(InlineKeyboardButton("Next", callback_data=f"navigate_comments:{city_name}:{page+1}"))
    reply_markup = InlineKeyboardMarkup([button_list]) if button_list else None
    if update.callback_query:
        message.edit_text(message_text, reply_markup=reply_markup)
    else:
        message.reply_text(message_text, reply_markup=reply_markup)

def show_comments_for_city(update, context, city_name, page):
    connection = context.bot_data.get('db_connection')
    if not connection:
        update.message.reply_text("Database connection is not available.")
        return
    with connection.cursor() as cursor:
        offset = page * COMMENTS_PER_PAGE
        cursor.execute(
            """
            SELECT comment, user_tg FROM public.cities WHERE city_name = %s
            ORDER BY created_at DESC LIMIT %s OFFSET %s;
            """,
            (city_name, COMMENTS_PER_PAGE, offset)
        )
        comments = cursor.fetchall()

        if not comments and page == 0:
            text = f"No comments found for {city_name}."
        elif not comments:
            text = "No more comments."
        else:
            cursor.execute("SELECT AVG(score) FROM public.cities WHERE city_name = %s;", (city_name,))
            avg_score = cursor.fetchone()[0]
            avg_score_text = f"Average score for {city_name}: {avg_score:.2f}\n" if avg_score else "No scores yet.\n"

            comments_text = "\n".join([f"{idx + 1 + offset}. {comment[0]} (User: {comment[1] or 'Unknown'})"
                                       for idx, comment in enumerate(comments)])
            text = f"{avg_score_text}Comments for {city_name}:\n\n{comments_text}"
        button_list = []
        if page > 0:
            button_list.append(InlineKeyboardButton("Previous", callback_data=f"navigate_comments:{city_name}:{page-1}"))
        if len(comments) == COMMENTS_PER_PAGE:
            button_list.append(InlineKeyboardButton("Next", callback_data=f"navigate_comments:{city_name}:{page+1}"))

        reply_markup = InlineKeyboardMarkup([button_list]) if button_list else None
        if update.callback_query:
            update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
        else:
            update.message.reply_text(text=text, reply_markup=reply_markup)

def handle_navigation(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    callback_data = query.data.split(':')
    _, city_name, page = callback_data
    page = int(page)
    if page < 0:
        page = 0
    show_comments_for_city(update, context, city_name, page)