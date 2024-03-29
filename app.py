from dispatcher import main as dispatcher_main
from chatbot_func.chatbot import main as chatbot1_main
from chatbot_func.chatbot import main as chatbot2_main

import os


if __name__ == '__main__':
    bot_type = os.getenv('BOT_TYPE')
    
    if bot_type == 'DISPATCHER':
        dispatcher_main()
    elif bot_type == 'CHATBOT1':
        chatbot1_main()
    elif bot_type == 'CHATBOT2':
        chatbot2_main()
    else:
        print("No BOT_TYPE specified or BOT_TYPE is invalid.")