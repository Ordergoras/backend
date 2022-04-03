from typing import Tuple, List, Dict
import mysql.connector
import os
import json


class DatabaseIO:
    cnx = None

    def establishConnection(self) -> None:
        try:
            self.cnx = mysql.connector.connect(user=os.getenv('dbUser'), password=os.getenv('dbPass'),
                                               host=os.getenv('dbHost'), database=os.getenv('dbName'))
        except mysql.connector.Error as error:
            print('DatabaseIO.establishConnection', error)

    def insertStorageData(self, values: Tuple[str, int]) -> None:
        cursor = None
        try:
            self.establishConnection()

            sql = "INSERT INTO storage (name, amount) VALUES (%s, %s) ON DUPLICATE KEY UPDATE amount = amount + VALUES(amount)"

            cursor = self.cnx.cursor()
            cursor.execute(sql, values)
            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.insertStorageData', error)
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

    def updateStorageData(self, values: Tuple[int, int]) -> None:
        cursor = None
        try:
            self.establishConnection()

            sql = "UPDATE storage SET amount = amount + " + str(values[1]) + " WHERE id = '" + str(values[0]) + "'"

            cursor = self.cnx.cursor()
            cursor.execute(sql)
            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.updateStorageData', error)
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

    def retrieveItemsFromStorage(self, retrievedItems: List[Tuple[int, int]]) -> List[Tuple[str, int]] | None:
        cursor = None
        try:
            self.establishConnection()

            for itemTuple in retrievedItems:
                sql = "UPDATE storage SET amount = amount - " + str(itemTuple[1]) + " WHERE id = '" + str(itemTuple[0]) + "'"

                cursor = self.cnx.cursor()
                cursor.execute(sql)

            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.retrieveItemsFromStorage', error)
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
                sql = "SELECT * FROM storage WHERE id = '" + str(itemId) + "'"

                cursor = self.cnx.cursor()
                cursor.execute(sql)
                result.append(cursor.fetchone())

            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.getStorageItemData', error)
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
            print('DatabaseIO.getStorageFullData', error)
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
            print('DatabaseIO.insertOrderData', error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        self.retrieveItemsFromStorage(values[2])
        return rowId

    def getOrder(self, orderId: int) -> Dict | None:
        cursor = None
        try:
            self.establishConnection()

            sql = "SELECT * FROM orders WHERE order_id = '" + str(orderId) + "'"

            cursor = self.cnx.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()

            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.getOrder', error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return {'orderId': result[0], 'tableNr': result[1], 'staffId': result[2], 'orderedItems': json.loads(result[3])}

    def insertNewAccount(self, staffId: str,  name: str, password: str, salt: str) -> bool:
        cursor = None
        try:
            self.establishConnection()

            sql = "INSERT INTO staff (staff_id, name, is_admin, password, salt) VALUES (%s, %s, %s, %s, %s)"

            values = (staffId, name, False, password, salt)

            cursor = self.cnx.cursor()
            cursor.execute(sql, values)
            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.insertNewAccount', error)
            return False
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return True

    def getAccountById(self, staffId: str) -> Dict | None:
        cursor = None
        try:
            self.establishConnection()

            sql = "SELECT * FROM staff WHERE staff_id = '" + staffId + "'"

            cursor = self.cnx.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()

            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.getAccountById', error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return {'staffId': result[0], 'name': result[1], 'isAdmin': result[2]}

    def getAccountByNameWithAuthData(self, name: str) -> Dict | None:
        cursor = None
        try:
            self.establishConnection()

            sql = "SELECT * FROM staff WHERE name = '" + name + "'"

            cursor = self.cnx.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()

            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.getAccountByNameWithAuthData', error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return {'staffId': result[0], 'name': result[1], 'isAdmin': result[2], 'password': result[3], 'salt': result[4]}

    def setAdminStatus(self, staffId: str, newStatus: bool) -> Dict | None:
        cursor = None
        try:
            self.establishConnection()

            sql = "UPDATE staff SET is_admin = " + str(newStatus) + " WHERE staff_id = '" + str(staffId) + "'"

            cursor = self.cnx.cursor()
            cursor.execute(sql)

            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.setAdminStatus', error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return self.getAccountById(staffId)
