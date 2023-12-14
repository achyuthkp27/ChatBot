import psycopg2

from config import config


def AccountListConnect():
    cssStyle = "<p>Here's an overview of your account and current balance</p><br><div class=container><div class=card style=\"background-image: linear-gradient( 109.6deg,  rgba(15,2,2,1) 11.2%, rgba(36,163,190,1) 91.1% );\"><span class=circle></span><div class=top-div><div class=credit-card-text>{}</div><div class=plus-sign><span></span> <span></span></div></div><div class=card-details><div class=card-number>{}</div><div class=balance-text><p>Available balance</p>TTD.<span class=actual-balance>{}</span></div></div></div></div>"
    connection = None
    try:
        params = config()
        print('Connecting to the postgreSQL database ...')
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()

        select_query: str = "select account_type,account_number,balance from chatbot.account_list where party_id='1058'"
        cursor.execute(select_query)
        records = cursor.fetchone()
        maskedNum = "**** **** " + records[1][-4:]
        print(records)
        return cssStyle.format(records[0], maskedNum, records[2])
        cursor.close()
        return cache_records
    except(Exception, psycopg2.DatabaseError) as error:
        print(f'Error during database connection: {error}')
    finally:
        if connection is not None:
            connection.close()
            print('Database connection terminated.')
