from typing import Tuple, List, Dict
import mysql.connector
import os
import json
import time


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

        return {a: {'name': b, 'amount': c} for a, b, c in result}

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

        return {a: {'name': b, 'amount': c} for a, b, c in result}

    def insertOrderData(self, values: Tuple[int, int, List[Tuple[int, int]]]) -> int | None:
        cursor = None
        try:
            self.establishConnection()

            sql = "INSERT INTO orders (table_nr, staff_id, ordered_items) VALUES (%s, %s, %s)"

            cursor = self.cnx.cursor()
            cursor.execute(sql, (values[0], values[1], json.dumps(values[2])))
            rowId = cursor.lastrowid
            self.cnx.commit()

        except mysql.connector.Error as error:
            print(error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        self.retrieveItemFromStorage(values[2])
        return rowId

    def getOrder(self, orderId: int) -> Dict | None:
        cursor = None
        try:
            self.establishConnection()

            sql = "SELECT * FROM orders WHERE order_id = " + str(orderId)

            cursor = self.cnx.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()

            self.cnx.commit()

        except mysql.connector.Error as error:
            print(error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return {result[0]: {'tableNr': result[1], 'staffId': result[2], 'orderedItems': json.loads(result[3])}}

    def insertNewAccount(self, userData: Tuple[str, str]) -> int | None:
        cursor = None
        try:
            self.establishConnection()

            sql = "INSERT INTO staff (name, is_admin, password, salt) VALUES (%s, %s, %s, %s)"

            salt = int(time.time())

            values = (userData[0], False, userData[1], salt)

            cursor = self.cnx.cursor()
            cursor.execute(sql, values)
            rowId = cursor.lastrowid
            self.cnx.commit()

        except mysql.connector.Error as error:
            print(error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return rowId

    def getAccount(self, staffId: int) -> Dict | None:
        cursor = None
        try:
            self.establishConnection()

            sql = "SELECT * FROM staff WHERE staff_id = " + str(staffId)

            cursor = self.cnx.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()

            self.cnx.commit()

        except mysql.connector.Error as error:
            print(error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return {result[0]: {'name': result[1], 'isAdmin': result[2]}}

    def setAdminStatus(self, executorId: int, staffId: int, newStatus: bool) -> Dict | None:
        executorIsAdmin = self.getAccount(executorId)[executorId]['isAdmin']

        if not executorIsAdmin:
            return {"You can't perform this action": "Restricted access"}

        cursor = None
        try:
            self.establishConnection()

            sql = "UPDATE staff SET is_admin = " + str(newStatus) + " WHERE staff_id = " + str(staffId)

            cursor = self.cnx.cursor()
            cursor.execute(sql)

            self.cnx.commit()

        except mysql.connector.Error as error:
            print(error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return self.getAccount(staffId)
