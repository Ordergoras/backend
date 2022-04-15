from datetime import datetime
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

    def insertStorageData(self, itemId: str, name: str, amount: int, group: ItemGroup, price: float) -> bool:
        cursor = None
        try:
            self.establishConnection()

            sql = "INSERT INTO storage (id, name, amount, `group`, price) VALUES (%s, %s, %s, %s, %s)"

            cursor = self.cnx.cursor()
            cursor.execute(sql, (itemId, name, amount, group, price))
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

            sql = "UPDATE storage SET amount = amount + {diff} WHERE id = '{itemId}'".format(diff=str(amountChange), itemId=itemId)

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
                sql = "UPDATE storage SET amount = amount - {diff} WHERE id = '{key}'".format(diff=str(value), key=key)

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

    def getStorageItemData(self, itemIds: List[str]) -> List[Dict[str, Union[str, int, ItemGroup]]] | None:
        cursor = None
        result = []
        try:
            self.establishConnection()

            for itemId in itemIds:
                sql = "SELECT * FROM storage WHERE id = '{itemId}'".format(itemId=itemId)

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

        if result is None:
            return None

        return [{'itemId': a, 'name': b, 'amount': c, 'group': d, 'price': e} for a, b, c, d, e in result]

    def getStorageFullData(self) -> List[Dict[str, Union[str, int, ItemGroup]]] | None:
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

        if result is None:
            return None

        return [{'itemId': a, 'name': b, 'amount': c, 'group': d, 'price': e} for a, b, c, d, e in result]

    def getItemIdMap(self) -> Dict[str, str] | None:
        cursor = None
        result = []
        try:
            self.establishConnection()

            sql = "SELECT id, `name` FROM storage"

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

        if result is None:
            return None

        return {a: b for a, b in result}

    def insertOrderData(self, orderId: str, tableId: int, staffId: str, orderedItems: Dict[str, int], completedItems: Dict[str, int]) -> bool:
        cursor = None
        try:
            self.establishConnection()

            sql = """INSERT INTO orders (order_id, table_nr, staff_id, ordered_items, completed_items, created_at) 
                     VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"""

            cursor = self.cnx.cursor()
            cursor.execute(sql, (orderId, tableId, staffId, json.dumps(orderedItems), json.dumps(completedItems)))
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

    def getOrder(self, orderId: str) -> Dict[str, Union[str, int, Dict[str, int], datetime]] | None:
        cursor = None
        try:
            self.establishConnection()

            sql = """SELECT order_id, table_nr, orders.staff_id, `name`, ordered_items, completed_items, created_at, completed FROM 
                     orders, staff WHERE orders.staff_id = staff.staff_id AND orders.order_id = '{orderId}'""".format(orderId=orderId)

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

        if result is None:
            return None

        return {
            'orderId': result[0],
            'tableNr': result[1],
            'staffId': result[2],
            'staffName': result[3],
            'orderedItems': json.loads(result[4]),
            'completedItems': json.loads(result[5]),
            'createdAt': result[6],
            'completed': result[7]
        }

    def getMyOrders(self, staffId: str) -> List[Dict[str, Union[str, int, Dict[str, int], datetime]]] | None:
        cursor = None
        try:
            self.establishConnection()

            sql = """SELECT order_id, table_nr, orders.staff_id, `name`, ordered_items, completed_items, created_at, completed FROM 
                     orders, staff WHERE orders.staff_id = staff.staff_id AND orders.staff_id = '{staffId}'""".format(staffId=staffId)

            cursor = self.cnx.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()

            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.getMyOrders', error)
            return None
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        if result is None:
            return None

        return [
            {'orderId': a,
             'tableNr': b,
             'staffId': c,
             'staffName': d,
             'orderedItems': json.loads(e),
             'completedItems': json.loads(f),
             'createdAt': g,
             'completed': h
             } for a, b, c, d, e, f, g, h in result
        ]

    def updateCompletedItems(self, orderId: str, itemId: str, increaseCompleted: bool) -> bool:
        cursor = None
        try:
            self.establishConnection()

            sqlIncrease = """
                            UPDATE orders SET completed_items = JSON_SET(completed_items, '$."{itemId}"', 
                            CAST(FORMAT(JSON_EXTRACT(completed_items, '$."{itemId}"') + 1, 0) AS UNSIGNED)) 
                            WHERE order_id = '{orderId}'
                          """.format(orderId=orderId, itemId=itemId)

            sqlDecrease = """
                            UPDATE orders SET completed_items = JSON_SET(completed_items, '$."{itemId}"', 
                            CAST(FORMAT(JSON_EXTRACT(completed_items, '$."{itemId}"') - 1, 0) AS UNSIGNED)) 
                            WHERE order_id = '{orderId}'
                          """.format(orderId=orderId, itemId=itemId)

            cursor = self.cnx.cursor()
            cursor.execute(sqlIncrease if increaseCompleted else sqlDecrease)
            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.updateCompletedItems', error)
            return False
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return True

    def completeOrder(self, orderId: str, isCompleted: bool) -> bool:
        cursor = None
        try:
            self.establishConnection()

            sql = "UPDATE orders SET completed = {isCompleted} WHERE order_id = '{orderId}'".format(isCompleted=isCompleted, orderId=orderId)

            cursor = self.cnx.cursor()
            cursor.execute(sql)
            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.completeOrder', error)
            return False
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        return True

    def checkIfOrderComplete(self, orderId: str) -> True | False:
        cursor = None
        try:
            self.establishConnection()

            sql = "SELECT ordered_items, completed_items FROM orders WHERE order_id = '{orderId}'".format(orderId=orderId)

            cursor = self.cnx.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()

            self.cnx.commit()

        except mysql.connector.Error as error:
            print('DatabaseIO.checkIfOrderComplete', error)
            return False
        finally:
            if self.cnx.is_connected():
                self.cnx.close()
            if cursor is not None:
                cursor.close()

        if result is None:
            return False

        orderedItems = json.loads(result[0])
        completedItems = json.loads(result[1])

        for key in orderedItems.keys():
            if completedItems[key] != orderedItems[key]:
                return False

        return True

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

            sql = "SELECT * FROM staff WHERE staff_id = '{staffId}'".format(staffId=staffId)

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

        if result is None:
            return None

        return {'staffId': result[0], 'name': result[1], 'isAdmin': bool(result[2])}

    def getAccountByNameWithAuthData(self, name: str) -> Dict[str, Union[str, bool]] | None:
        cursor = None
        try:
            self.establishConnection()

            sql = "SELECT * FROM staff WHERE name = '{name}'".format(name=name)

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

        if result is None:
            return None

        return {'staffId': result[0], 'name': result[1], 'isAdmin': bool(result[2]), 'password': result[3], 'salt': result[4]}

    def setAdminStatus(self, staffId: str, newStatus: bool) -> Dict[str, Union[str, bool]] | None:
        cursor = None
        try:
            self.establishConnection()

            sql = "UPDATE staff SET is_admin = {newStatus} WHERE staff_id = '{staffId}'".format(newStatus=str(newStatus), staffId=staffId)

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

            sql = "INSERT INTO sessions (session_id, staff_id, created_at) VALUES (%s, %s, CURRENT_TIMESTAMP)"

            cursor = self.cnx.cursor()
            cursor.execute(sql, (sessionId, staffId))
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

            sql = "DELETE FROM sessions WHERE session_id = '{sessionId}'".format(sessionId=sessionId)

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

    def getSession(self, sessionId: str) -> Dict[str, Union[str, bool, datetime]] | None:
        cursor = None
        try:
            self.establishConnection()

            sql = "SELECT * FROM sessions WHERE session_id = '{sessionId}'".format(sessionId=sessionId)

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

        if result is None:
            return None

        return {'sessionId': result[0], 'staffId': result[1], 'createdAt': result[2]}
