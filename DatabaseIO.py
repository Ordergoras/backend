from typing import Tuple
import mysql.connector
import os


class DatabaseIO:
    cnx = None

    def establishConnection(self) -> None:
        try:
            self.cnx = mysql.connector.connect(user=os.getenv('dbUser'), password=os.getenv('dbPass'),
                                               host='127.0.0.1', database=os.getenv('dbName'))
        except mysql.connector.Error as error:
            print(error)

    def insertStorageData(self, values: Tuple[str, int]) -> None:
        cursor = None
        try:
            self.establishConnection()

            add_item = "INSERT INTO storage (name, amount) VALUES (%s, %s) ON DUPLICATE KEY UPDATE amount = amount + VALUES(amount)"

            cursor = self.cnx.cursor()
            cursor.execute(add_item, values)
            self.cnx.commit()

        except mysql.connector.Error as error:
            print(error)
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()
