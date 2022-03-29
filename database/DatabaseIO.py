from typing import Tuple, List, Dict
import mysql.connector
import os
import json


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

            sql = "INSERT INTO storage (name, amount) VALUES (%s, %s) ON DUPLICATE KEY UPDATE amount = amount + VALUES(amount)"

            cursor = self.cnx.cursor()
            cursor.execute(sql, values)
            self.cnx.commit()

        except mysql.connector.Error as error:
            print(error)
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

    def updateStorageData(self, values: Tuple[int, int]) -> None:
        cursor = None
        try:
            self.establishConnection()

            sql = "UPDATE storage SET amount = amount + " + str(values[1]) + " WHERE id =" + str(values[0])

            cursor = self.cnx.cursor()
            cursor.execute(sql)
            self.cnx.commit()

        except mysql.connector.Error as error:
            print(error)
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

    def retrieveItemFromStorage(self, retrievedItems: List[Tuple[int, int]]) -> List[Tuple[str, int]] | None:
        cursor = None
        try:
            self.establishConnection()

            for itemTuple in retrievedItems:
                sql = "UPDATE storage SET amount = amount - " + str(itemTuple[1]) + " WHERE id = " + str(itemTuple[0])

                cursor = self.cnx.cursor()
                cursor.execute(sql)

            self.cnx.commit()

        except mysql.connector.Error as error:
            print(error)
            # TODO error handling
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return self.getStorageItemData([item[0] for item in retrievedItems])

    def getStorageItemData(self, itemIds: List[int]) -> Dict | None:
        cursor = None
        result = []
        try:
            self.establishConnection()

            for itemId in itemIds:
                sql = "SELECT * FROM storage WHERE id = " + str(itemId)

                cursor = self.cnx.cursor()
                cursor.execute(sql)
                result.append(cursor.fetchone())

            self.cnx.commit()

        except mysql.connector.Error as error:
            print(error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return {a: (b, c) for a, b, c in result}

    def getStorageFullData(self) -> Dict | None:
        cursor = None
        result = []
        try:
            self.establishConnection()

            sql = "SELECT * FROM storage"

            cursor = self.cnx.cursor()
            cursor.execute(sql)

            for row in cursor:
                result.append(row)

            self.cnx.commit()

        except mysql.connector.Error as error:
            print(error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return {a: (b, c) for a, b, c in result}

    def insertOrderData(self, values: Tuple[int, int, List[Tuple[int, int]]]) -> None:
        cursor = None
        try:
            self.establishConnection()

            sql = "INSERT INTO orders (table_nr, staff_id, ordered_items) VALUES (%s, %s, %s)"

            cursor = self.cnx.cursor()
            cursor.execute(sql, (values[0], values[1], json.dumps(values[2])))
            self.cnx.commit()

        except mysql.connector.Error as error:
            print(error)
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        self.retrieveItemFromStorage(values[2])
