import os
import requests
from dotenv import load_dotenv
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

#load env
load_dotenv()

class ChatGPT():
    def submit(self, message):   
        conversation = [{"role": "user", "content": message}]
        url = os.getenv('CHATGPT_BASICURL') + "/deployments/" + os.getenv('CHATGPT_MODELNAME') + "/chat/completions/?api-version=" + os.getenv('CHATGPT_APIVERSION')
        headers = { 'Content-Type': 'application/json', 'api-key': os.getenv('CHATGPT_ACCESS_TOKEN') }
        payload = {'messages': conversation}
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f'Error: {response.status_code}, {response.reason}'
        
def equiped_chatgpt(update: Update, context: CallbackContext) -> None:
    try:
        processing_message = context.bot.send_message(chat_id=update.effective_chat.id, text="Processing your request...")
        logging.info(f"Received prompt: '{update.message.text}', Sent 'Processing your request...' message to user.")
        chatgpt = context.bot_data['chatgpt']
        reply_message = chatgpt.submit(update.message.text)
        logging.info(f"Received reply from chatgpt.submit: {reply_message}")
        
        if reply_message.startswith('Error:'):
            context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
        else:
            context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_message.message_id,
                text=reply_message
            )
    except Exception as e:
        logging.error(f"An exception occurred in equiped_chatgpt: {e}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred while processing your request.")

if __name__ == '__main__':
    ChatGPT_test = ChatGPT()

    while True:
        user_input = input("Typing anything to ChatGPT:\t")
        response = ChatGPT_test.submit(user_input)
        print(response)