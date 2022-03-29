import mysql.connector
import os

cnx = mysql.connector.connect(user=os.getenv('dbUser'), password=os.getenv('dbPass'),
                              host='127.0.0.1',
                              database=os.getenv('dbName'))

curser = cnx.cursor()

try:
    add_item = "INSERT INTO storage (name, amount) VALUES (%s, %s) ON DUPLICATE KEY UPDATE amount = amount + VALUES(amount)"
    values = ('Brötchen', 500)

    curser.execute(add_item, values)
    cnx.commit()

except mysql.connector.Error as error:
    print(error)
finally:
    if cnx.is_connected():
        curser.close()
        cnx.close()
