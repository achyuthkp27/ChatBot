import time

import psycopg2

from config import config

user_data = {
    "account_number": None,
    "delivery_options": None,
    "chequebook_size": None,
    "otp_check": None,
    "otp_count": 0
}

DELIVERY_OPTIONS = ['collect in branch', 'delivery to address', 'address', 'branch', '1', '2']
CHEQUEBOOK_SIZES = ['25', '50', '75', '1', '2', '3']
delivery_option_map = {
    'collect in branch': 'Collect in Branch',
    'branch': 'Collect in Branch',
    '1': 'Collect in Branch',
    'delivery to address': 'Delivery to Address',
    'address': 'Delivery to Address',
    '2': 'Delivery to Address'
}

cheque_leave_map = {
    '1': '25',
    '25': '25',
    '2': '50',
    '50': '50',
    '3': '75',
    '75': '75'
}


def ClearInputs():
    user_data.update({
        "account_number": None,
        "delivery_options": None,
        "chequebook_size": None,
        "otp_check": None,
        "otp_count": 0
    })

MAX_OTP_ATTEMPTS = 3

def cheque_book_request(ip):
    if user_data['otp_count'] >= MAX_OTP_ATTEMPTS:
        return "Maximum OTP attempts reached. Please try again after some time."

    if ip is None and user_data['account_number'] is None:
        return "Please provide your Account Number or send '<b>Abort</b>' to stop the process"

    if user_data['account_number'] is None:
        return handle_account_number(ip)

    if user_data['delivery_options'] is None:
        return handle_delivery_options(ip)

    if user_data['chequebook_size'] is None:
        return handle_chequebook_size(ip)

    if user_data['otp_check'] is None:
        return handle_otp_check(ip)

    return "Completed"

def handle_account_number(ip):
    valid_account_numbers = ["289131966543", "335131962556"]
    if ip in valid_account_numbers:
        if not check_cheque_book(ip):
            user_data['account_number'] = ip
            return "Please provide delivery details: <p> 1. Collect in Branch</p><p> 2. Delivery to Address</p>"
        else:
            return "Cheque Book Order already exists for this Account Number."
    else:
        return "Invalid Account Details provided. Please enter your Account Number"

def handle_delivery_options(ip):
    if ip.lower() in DELIVERY_OPTIONS:
        user_data['delivery_options'] = ip
        return "Please provide number of Cheque Leaves required <p> 1. 25</p><p> 2. 50</p> <p>3. 75</p>"
    else:
        return "Invalid details provided. Please enter a Delivery Option"

def handle_chequebook_size(ip):
    if ip.isdigit() and ip in CHEQUEBOOK_SIZES:
        user_data['chequebook_size'] = ip
        return "We have sent an OTP to your Registered device. Please enter the sent OTP"
    else:
        return "Invalid details provided. Please enter a valid Cheque Leave Size"

def handle_otp_check(ip):
    if ip.isdigit() and ip == "567876":
        user_data['otp_check'] = ip
        cheque_book_connect()
        return "Completed"
    else:
        user_data['otp_count'] += 1
        return "Invalid OTP provided"



def check_cheque_book(ip):
    connection = None
    try:
        params = config()
        print('Connecting to the postgreSQL database ...')
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()

        select_query: str = "select party_id from chatbot.cheque_order_details where party_id=%s and account_number=%s"
        cursor.execute(select_query, ("1058", ip))
        records = cursor.fetchone()
        time.sleep(1)
        cursor.close()
        return len(records) != 0
    except(Exception, psycopg2.DatabaseError) as error:
        print(f'Error during database connection: {error}')
    finally:
        if connection is not None:
            connection.close()
            print('Database connection terminated.')


def cheque_book_connect():
    connection = None
    try:
        params = config()
        print('Connecting to the postgreSQL database ...')
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()

        insert_query: str = "insert into chatbot.cheque_order_details(party_id,account_number,delivery_option,leaves) values (%s, %s, %s, %s)"
        delivery_option = delivery_option_map.get(user_data['delivery_options'].lower(), 'Delivery to Address')
        cheque_leave = cheque_leave_map.get(user_data['chequebook_size'], 'Invalid Size')
        cursor.execute(insert_query,
                       ("1058", user_data['account_number'], delivery_option,
                        cheque_leave))
        connection.commit()
        time.sleep(1)
        cursor.close()
    except(Exception, psycopg2.DatabaseError) as error:
        print(f'Error during database connection: {error}')
    finally:
        if connection is not None:
            connection.close()
            print('Database connection terminated.')
        ClearInputs()


def cheque_book_details():
    connection = None
    try:
        params = config()
        print('Connecting to the postgreSQL database ...')
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()

        cursor.execute(
            "select account_number,delivery_option,leaves,order_date from chatbot.cheque_order_details where party_id='1058'")
        records = cursor.fetchall()
        print(records)
        cursor.close()
        connection.close()

        if len(records) == 0:
            return "No Cheque Book Order History Found"
        else:
            header = "<h4 class=cheque-book>Cheque Book Order Details</h4><br><div class=container>"
            row = "<div class=cheque-details><div class=detail><span class=label>Account Number:</span> <span class=value>{}</span></div><div class=detail><span class=label>Cheque Book Size:</span> <span class=value>{}</span></div><div class=detail><span class=label>Delivery Option:</span> <span class=value>{}</span></div><div class=detail><span class=label>Ordered Date:</span> <span class=value>{}</span></div></div><br><br>"
            end = "</div>"
            finalRow = ""
            for i in records:
                print(i)
                finalRow = finalRow + row.format(i[0], i[2], i[1], i[3])
            return header + finalRow + end
    except(Exception, psycopg2.DatabaseError) as error:
        print(f'Error during database connection: {error}')
    finally:
        if connection is not None:
            connection.close()
            print('Database connection terminated.')
