import time

import psycopg2

from config import config


def CreditCardConnect():
    cssStyle = "<p>Here's a breakdown of your credit card and corresponding outstanding balance</p><br><div class=container><div class=card style=\"background-image:linear-gradient(to right top,#1d3634,#2c514c)\"><span class=circle></span><div class=top-div><div class=credit-card-text>Credit Card</div><div class=plus-sign><span></span> <span></span></div></div><div class=card-details><div class=card-number>{}</div><div class=balance-text><p>Outstanding balance</p>TTD.<span class=actual-balance>{}</span></div></div><div class=ownername><span>{}</span><h2>{}</h2></div></div></div>"
    connection = None
    try:
        params = config()
        print('Connecting to the postgreSQL database ...')
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()

        select_query: str = "select card_type ,card_number ,balance,card_holder from chatbot.credit_card_list where party_id='1058'"
        cursor.execute(select_query)
        records = cursor.fetchone()
        maskedNum = "**** **** **** " + records[1][-4:]
        print(records)
        time.sleep(1)
        cursor.close()
        return cssStyle.format(maskedNum, records[2], records[3], records[0])
    except(Exception, psycopg2.DatabaseError) as error:
        print(f'Error during database connection: {error}')
    finally:
        if connection is not None:
            connection.close()
            print('Database connection terminated.')
