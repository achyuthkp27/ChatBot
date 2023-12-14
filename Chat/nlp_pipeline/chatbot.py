import json
import os
import random
import secrets
from datetime import datetime

import torch

from nlp_pipeline.databaseOp.accountList import AccountListConnect
from nlp_pipeline.databaseOp.chequeBookReq import ChequeBookReq, ChequeBookDetails,ClearInputs
from nlp_pipeline.databaseOp.creditCardList import CreditCardConnect
from nlp_pipeline.databaseOp.debitCardList import DebitCardConnect
from nlp_pipeline.model import NeuralNetwork
from nlp_pipeline.nltk_lib import bag_of_words, tokenizer

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
error_messages = [
    "I'm not sure I understand. Can you rephrase that?",
    "Could you provide more details? I'm still learning!",
    "Hmm, I'm having trouble understanding. Can you try again?",
    "Sorry, I didn't catch that. Could you say it differently?",
    "Sorry I didn't understand! I'm still under development. My knowledge is limited"
]

try:
    with open('./nlp_pipeline/training data/intents.json', 'r') as json_data:
        intents = json.load(json_data)

    FILE = "./nlp_pipeline/data.pth"
    data = torch.load(FILE)
except FileNotFoundError:
    print("Required files not found. Please check the file paths.")

input_size = data["input_size"]
hidden_size = data["hidden_size"]
num_classes = data["num_classes"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNetwork(input_size, hidden_size, num_classes).to(device)
model.load_state_dict(model_state)
model.eval()

dbFunctionalities = ["creditCard", "debitCard", "accountList", "accountStatement", "chequeBookReq", "fundTransfer",
                     "chequeBookDetails"]
dbHashMap = {
    "creditCard": CreditCardConnect(),
    "debitCard": DebitCardConnect(),
    "accountList": AccountListConnect()
}

chequeBookReq: bool = False


# Function to log low-confidence inputs
def log_low_confidence_input(inp, confidence, predicted):
    folder_name = "unknown_input_log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"Time: {timestamp}, Input: {inp}, Confidence: {confidence:.4f}, Predicted: {predicted}\n"
    file_name = os.path.join(folder_name, "low_confidence_inputs.log")

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    logging.basicConfig(filename=file_name, level=logging.INFO)
    logger = logging.getLogger()

    try:
        logger.info(log_entry)
    except Exception as e:
        logger.error(f"Error logging low confidence input: {e}")



def databaseFunc(ip):
    return dbHashMap[ip] if ip in dbFunctionalities else None


def BankFaqChatBot(inp):
    global chequeBookReq
    if chequeBookReq:
        if inp.lower() == "abort":
            chequeBookReq = False
            ClearInputs()
            return "Cheque Book Request Aborted"

        cheqResp = ChequeBookReq(inp)
        if cheqResp == "Completed" or cheqResp == "Cheque Book Order Already Exist for this Account Number":
            chequeBookReq = False
            if cheqResp == "Completed":
                return "Cheque Book Ordered Successfully.<p> Your order reference Number is " + str(
                    secrets.randbelow(10 ** 9) + 10 ** 9) + "</p>"
        return cheqResp
    sentence = tokenizer(inp)
    data = bag_of_words(sentence, all_words)
    data = data.reshape(1, data.shape[0])
    data = torch.from_numpy(data).to(device)

    output = model(data)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    print(predicted)
    print(prob)
    if prob.item() > 0.80:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                bot_resp: str = random.choice(intent['responses'])
                if bot_resp == "chequeBookReq":
                    chequeBookReq = True
                    cheqResp = ChequeBookReq(None)
                    return cheqResp
                if bot_resp == "chequeBookDetails":
                    return ChequeBookDetails()
                return dbHashMap[bot_resp] if bot_resp in dbFunctionalities else bot_resp
        return "Sorry I didn't understand! I'm still under development. My knowledge is limited"

    else:
        guessed = ""
        for intent in intents['intents']:
            if tag == intent["tag"]:
                guessed = random.choice(intent['responses'])
        log_low_confidence_input(inp, prob.item(), guessed)
        return random.choice(error_messages)
