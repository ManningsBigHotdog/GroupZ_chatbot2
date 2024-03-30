from dotenv import load_dotenv
import logging
from telegram import Update
from telegram.ext import CallbackContext

#load env
load_dotenv()

def plan_trip(update: Update, context: CallbackContext) -> None:
    try:
        processing_message = context.bot.send_message(chat_id=update.effective_chat.id, text="Processing your request...")
        logging.info(f"Received prompt: '{update.message.text}', Sent 'Processing your request...' message to user.")

        city_name = None

        if update.callback_query:
            query = update.callback_query
            query.answer()
            callback_data = query.data.split(':')
            _, city_name, page = callback_data
            page = int(page)
        elif context.args:
            city_name = ' '.join(context.args)

        if not city_name:
            context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_message.message_id,
                text="Usage: /plantrip <City> e.g. /plantrip Tokyo"
            )
            return

        prompt = f"You are now a travel planner. Please list out 5 feature spots for a traveller visiting {city_name}."
        chatgpt = context.bot_data['chatgpt']
        reply_message = chatgpt.submit(prompt)
        logging.info(f"Received reply from chatgpt.submit: {reply_message}")

        if reply_message.startswith('Error:'):
            context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_message.message_id,
                text=reply_message
            )
        else:
            context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_message.message_id,
                text=reply_message
            )
            
    except Exception as e:
        logging.error(f"An exception occurred in plan_trip: {e}")
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_message.message_id,
            text="An error occurred while processing your request."
        )
