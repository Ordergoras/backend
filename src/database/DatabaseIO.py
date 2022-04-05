from typing import List, Dict, Union
import mysql.connector
import os
import json
from src.utils.types import ItemGroup


class DatabaseIO:
    cnx = None

    def establishConnection(self) -> None:
        try:
            self.cnx = mysql.connector.connect(user=os.getenv('dbUser'), password=os.getenv('dbPass'),
                                               host=os.getenv('dbHost'), database=os.getenv('dbName'))
        except mysql.connector.Error as error:
            print('DatabaseIO.establishConnection', error)

    def insertStorageData(self, itemId: str, name: str, amount: int, group: ItemGroup) -> bool:
        cursor = None
        try:
            self.establishConnection()

            sql = "INSERT INTO storage (id, name, amount, `group`) VALUES (%s, %s, %s, %s)"

            cursor = self.cnx.cursor()
            cursor.execute(sql, (itemId, name, amount, group))
            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.insertStorageData', error)
            return False
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return True

    def updateStorageData(self, itemId: str, amountChange: int) -> bool:
        cursor = None
        try:
            self.establishConnection()

            sql = "UPDATE storage SET amount = amount + " + str(amountChange) + " WHERE id = '" + itemId + "'"

            cursor = self.cnx.cursor()
            cursor.execute(sql)
            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.updateStorageData', error)
            return False
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return True

    def retrieveItemsFromStorage(self, retrievedItems: Dict[str, int]) -> Dict[str, Dict[str, int]] | None:
        cursor = None
        try:
            self.establishConnection()

            for key, value in retrievedItems.items():
                sql = "UPDATE storage SET amount = amount - " + str(value) + " WHERE id = '" + key + "'"

                cursor = self.cnx.cursor()
                cursor.execute(sql)

            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.retrieveItemsFromStorage', error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return self.getStorageItemData([key for key in retrievedItems.keys()])

    def getStorageItemData(self, itemIds: List[str]) -> Dict[str, Dict[str, int]] | None:
        cursor = None
        result = []
        try:
            self.establishConnection()

            for itemId in itemIds:
                sql = "SELECT * FROM storage WHERE id = '" + itemId + "'"

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

        return {a: {'name': b, 'amount': c, 'group': d} for a, b, c, d in result}

    def getStorageFullData(self) -> Dict[str, Dict[str, int]] | None:
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

        return {a: {'name': b, 'amount': c, 'group': d} for a, b, c, d in result}

    def insertOrderData(self, orderId: str, tableId: int, staffId: str, orderedItems: Dict[str, int], timestamp: float) -> bool:
        cursor = None
        try:
            self.establishConnection()

            sql = "INSERT INTO orders (order_id, table_nr, staff_id, ordered_items, timestamp) VALUES (%s, %s, %s, %s, %s)"

            cursor = self.cnx.cursor()
            cursor.execute(sql, (orderId, tableId, staffId, json.dumps(orderedItems), timestamp))
            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.insertOrderData', error)
            return False
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        self.retrieveItemsFromStorage(orderedItems)
        return True

    def getOrder(self, orderId: str) -> Dict[str, Union[str, int, Dict[str, int], float]] | None:
        cursor = None
        try:
            self.establishConnection()

            sql = "SELECT * FROM orders WHERE order_id = '" + orderId + "'"

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

        return {
            'orderId': result[0],
            'tableNr': result[1],
            'staffId': result[2],
            'orderedItems': json.loads(result[3]),
            'timestamp': result[4],
            'completed': result[5]
        }

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

    def getAccountById(self, staffId: str) -> Dict[str, Union[str, bool]] | None:
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

        return {'staffId': result[0], 'name': result[1], 'isAdmin': bool(result[2])}

    def getAccountByNameWithAuthData(self, name: str) -> Dict[str, Union[str, bool]] | None:
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

        return {'staffId': result[0], 'name': result[1], 'isAdmin': bool(result[2]), 'password': result[3], 'salt': result[4]}

    def setAdminStatus(self, staffId: str, newStatus: bool) -> Dict[str, Union[str, bool]] | None:
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

    def insertNewSession(self, sessionId: str, staffId: str) -> bool:
        cursor = None
        try:
            self.establishConnection()

            sql = "INSERT INTO sessions (session_id, staff_id, is_valid) VALUES (%s, %s, %s)"

            cursor = self.cnx.cursor()
            cursor.execute(sql, (sessionId, staffId, True))
            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.insertNewSession', error)
            return False
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return True

    def deleteSession(self, sessionId: str) -> bool:
        cursor = None
        try:
            self.establishConnection()

            sql = "DELETE FROM sessions WHERE session_id = '" + sessionId + "'"

            cursor = self.cnx.cursor()
            cursor.execute(sql)
            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.deleteSession', error)
            return False
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return True

    def getSession(self, sessionId: str) -> Dict[str, Union[str, bool]] | None:
        cursor = None
        try:
            self.establishConnection()

            sql = "SELECT * FROM sessions WHERE session_id = '" + sessionId + "'"

            cursor = self.cnx.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()

            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.getSession', error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return {'sessionId': result[0], 'staffId': result[1], 'isValid': result[2]}
