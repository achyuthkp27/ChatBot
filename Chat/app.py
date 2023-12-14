import os
from datetime import datetime

import numpy as np
from flask import Flask, render_template, request, jsonify

from nlp_pipeline.chatbot import BankFaqChatBot

goodbye_responses = ["Have a good day", "Bye", "Goodbye", "Hope to meet soon", "peace out!",
                     "Sure, leaving now!", "Alright, exiting the chat.", "Got it, closing the chat."]
error_response = ["Apologies, I encountered an issue. Could you please try again?",
                  "I seem to have run into a problem. Let's try that once more.",
                  "Oops! Something went wrong. Can you rephrase your query?"]


class ChatBot():
    def __init__(self):
        print("----- FIS ChatBot -----")
        self.log_folder = 'log'
        self.log_name = 'BankFAQChatBot_log_'
        self.file_name = os.path.join(self.log_folder,
                                      self.log_name + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log")

        self.create_log_folder()

    def create_log_folder(self):
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)
        with open(self.file_name, "w") as file:
            file.write("Bank FAQ ChatBot-> \n")

     def log_conversation(self, user_input, response):
        logger = logging.getLogger(__name__)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(self.file_name)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

        if not os.path.exists(self.log_folder):
            self.create_log_folder()

        if user_input:
            logger.info("User -> %s", user_input)
        logger.info("AI -> %s", response)

    # Returns NLP response
    def chat(self, text):
        chat = BankFaqChatBot(text)
        log_conversation(self,text,chat)
        return chat


def start_chat(user_input):
    ai = ChatBot()

    if any(i in user_input for i in ["quit", "exit", "close", "shut down", "bye"]):
        return np.random.choice(goodbye_responses)
    else:
        output = ai.chat(user_input)
        return output


app = Flask(__name__)
app.static_folder = 'static'


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    try:
        userText = request.args.get('msg')
        return start_chat(userText)
    except ValueError:
        return np.random.choice(error_response)


@app.route("/test", methods=['GET'])
def test():
    try:
        if request.method == 'GET':
            return jsonify({"response": "Get Request Called"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500        


@app.route("/testBotRespParam/<txt>", methods=['POST', 'GET'])
def testBotRespParam(txt):
    try:
        return jsonify({"response": start_chat(txt)})
    except ValueError:
        return np.random.choice(error_response)


@app.route("/testBotResp", methods=['POST'])
def testBotResp():
    try:
        if request.data:
            user_ip = request.get_json()
            return jsonify({"response": start_chat(user_ip["query"])})
        else:
            return jsonify({"response": "No Request Data Found"})
    except ValueError:  
        return np.random.choice(error_response)


if __name__ == "__main__":
    app.run(debug=True, port=9090)
