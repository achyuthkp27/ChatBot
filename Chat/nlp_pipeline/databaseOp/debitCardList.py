import time

import psycopg2

from config import config


def DebitCardConnect():
    cssStyle = "<p>Below is the details of your debit card along with available balance</p><br><div class=container><div class=card style=\"background-image: radial-gradient( circle farthest-corner at 10% 20%,  rgba(100,43,115,1) 0%, rgba(4,0,4,1) 90% );\"><span class=circle></span><div class=top-div><div class=credit-card-text>Debit Card</div><div class=plus-sign><span></span> <span></span></div></div><div class=card-details><div class=card-number>{}</div><div class=balance-text><p>Available balance</p>TTD.<span class=actual-balance>{}</span></div></div><div class=ownername><span>{}</span><h2>{}</h2></div></div></div>"
    connection = None
    try:
        params = config()
        print('Connecting to the postgreSQL database ...')
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()

        select_query: str = "select card_type ,card_number ,balance,card_holder from chatbot.debit_card_list where party_id='1058'"
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
