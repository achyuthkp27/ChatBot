import random
import time

import psycopg2

from config import config

main_account = {
                "account_type": "Savings",
                "account_number": "259944160429",
                "account_balance": "TTD. 435.00",
                "account_nickname": "Hira"
            }

def mask_account_number(account_number):
    masked = ''.join(['*' if char.isdigit() else char for char in account_number[:-4]]) + account_number[-4:]
    return ' '.join(masked[i:i + 4] for i in range(0, len(masked), 4))


def filter_accounts(ip, accounts):
    query = ip.lower().split()

    # Check if the query contains a number (potential account number)
    potential_numbers = [word for word in query if word.isdigit()]

    # Check if the query contains words related to nicknames
    potential_nicknames = [word for word in query if
                           any(word.lower() in acc["account_nickname"].lower() for acc in accounts)]

    # Check if the query contains words related to account types
    potential_account_types = [word for word in query if
                               any(word.lower() in acc["account_type"].lower() for acc in accounts)]
    # Filter accounts based on provided information
    filtered_accounts = []
    for acc in accounts:
        if (any(num in acc["account_number"] for num in potential_numbers)
                or any(nickname.lower() in acc["account_nickname"].lower() for nickname in potential_nicknames)
                or any(acc_type.lower() in acc["account_type"].lower() for acc_type in potential_account_types)):
            filtered_accounts.append(acc)
    masked_accounts = [
        {**acc, "account_number": mask_account_number(acc["account_number"])}
        if "account_number" in acc else acc
        for acc in (filtered_accounts if filtered_accounts else accounts)
    ]

    return masked_accounts


def AccountListConnect(ip: str):
    connection = None
    try:
        params = config()
        print('Connecting to the postgreSQL database ...')
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()

        select_query: str = "select account_type,account_number,balance,nick_name from chatbot.account_list where party_id='1058'"
        cursor.execute(select_query)
        records = cursor.fetchall()
        print(records)
        accounts = []
        for row in records:
            account = {
                "account_type": row[0],
                "account_number": row[1],
                "account_balance": row[2],
                "account_nickname": row[3]
            }
            accounts.append(account)
        time.sleep(1)
        cursor.close()

        return filter_accounts(ip, accounts)
    except(Exception, psycopg2.DatabaseError) as error:
        print(f'Error during database connection: {error}')
    finally:
        if connection is not None:
            connection.close()
            print('Database connection terminated.')
