import json
import logging
import os
from datetime import datetime

import torch

from nlp_pipeline.databaseOp.accountList import AccountListConnect
from nlp_pipeline.databaseOp.chequeBookReq import cheque_book_request, cheque_book_details, ClearInputs
from nlp_pipeline.databaseOp.creditCardList import CreditCardConnect
from nlp_pipeline.databaseOp.debitCardList import DebitCardConnect
from nlp_pipeline.nltk_lib import bag_of_words, tokenizer

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the error messages and the intents data from a JSON file
try:
    with open('./nlp_pipeline/config.json', 'r') as json_data:
        config = json.load(json_data)
        error_messages = config["error_messages"]
        intents = config["intents"]
        # Create a dictionary of tags and responses
        tag_dict = {intent["tag"]: intent["responses"] for intent in intents}
except FileNotFoundError as e:
    logging.error(f"Required files not found. Please check the file paths. {e}")
    exit()

# Load the model data from a file
try:
    FILE = "./nlp_pipeline/data.pth"
    data = torch.load(FILE)
except FileNotFoundError as e:
    logging.error(f"Required files not found. Please check the file paths. {e}")
    exit()

input_size = data["input_size"]
hidden_size = data["hidden_size"]
num_classes = data["num_classes"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

# Use PyTorch to create and load the model
model = torch.nn.Sequential(
    torch.nn.Linear(input_size, hidden_size),
    torch.nn.ReLU(),
    torch.nn.Linear(hidden_size, num_classes),
    torch.nn.Softmax(dim=1)
).to(device)
model.load_state_dict(model_state)
model.eval()

# Create a function to log low-confidence inputs
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

# Create a function to handle the chat bot logic
def BankFaqChatBot(inp):
    # Use a local variable to store the cheque book request status
    chequeBookReq = False

    if chequeBookReq:
        if inp.lower() == "abort":
            chequeBookReq = False
            ClearInputs()
            return "Cheque Book Request Aborted"

        cheqResp = cheque_book_request(inp)
        if cheqResp == "Completed" or cheqResp == "Cheque Book Order Already Exist for this Account Number":
            chequeBookReq = False
            if cheqResp == "Completed":
                return f"Cheque Book Ordered Successfully.<p> Your order reference Number is {secrets.randbelow(10 ** 9) + 10 ** 9}</p>"
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
    logging.debug(f"Predicted: {predicted}, Prob: {prob}")
    if prob.item() > 0.80:
        # Use the tag dictionary to get the response
        responses = tag_dict.get(tag, [])
        if responses:
            bot_resp = random.choice(responses)
            if bot_resp == "chequeBookReq":
                chequeBookReq = True
                cheqResp = cheque_book_request(None)
                return cheqResp
            elif bot_resp == "chequeBookDetails":
                return cheque_book_details()
            elif bot_resp == "creditCard":
                return CreditCardConnect()
            elif bot_resp == "debitCard":
                return DebitCardConnect()
            elif bot_resp == "accountList":
                return AccountListConnect()
            else:
                return bot_resp
        else:
            return "Sorry, I don't have an answer for that."
    else:
        # Log the low confidence input
        log_low_confidence_input(inp, prob.item(), tag)
        return random.choice(error_messages)

# Create a function to handle database operations
def databaseFunc(ip):
    # Use a dictionary to store the database connections
    dbHashMap = {
        "creditCard": CreditCardConnect(),
        "debitCard": DebitCardConnect(),
        "accountList": AccountListConnect()
    }
    return dbHashMap.get(ip, None) # Use the get method to return None if the key is not found


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