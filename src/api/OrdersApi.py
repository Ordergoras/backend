from typing import Dict
from flask import Blueprint, request
from src.database.DatabaseIO import DatabaseIO
from src.utils.authUtils import generateUuid, tokenRequired, validateUserInput
from src.utils.responseUtils import create400Response, create200Response, create200ResponseData

ordersApi = Blueprint('ordersApi', __name__)


@ordersApi.route('/postOrder', methods=['POST'])
@tokenRequired
def addNewOrder(staff, newAccessToken):
    tableNr: int = request.json.get('tableNr')
    orderedItems: Dict[str, int] = request.json.get('orderedItems')
    if tableNr is None or orderedItems is None:
        return create400Response(message='bErrorFieldCheck', newAccessToken=newAccessToken)
    elif not validateUserInput('orders', tableNr=tableNr, orderedItems=orderedItems):
        return create400Response(message='bErrorFieldInvalid')

    orderId = generateUuid()

    completedItems = {itemId: 0 for itemId in orderedItems.keys()}

    dbio = DatabaseIO()
    itemData = dbio.getStorageItemData([str(key) for key in orderedItems.keys()])

    price = 0
    for key in orderedItems:
        price += orderedItems[key] * next(item for item in itemData if item['itemId'] == key)['price']

    hasInserted = dbio.insertOrderData(orderId, tableNr, staff['staffId'], orderedItems, completedItems, price)

    if hasInserted:
        return create200ResponseData({'message': 'bSuccessOrderInsert', 'orderId': orderId}, newAccessToken=newAccessToken)
    else:
        return create400Response(message='bErrorOrderInsert', newAccessToken=newAccessToken)


@ordersApi.route('/getOrder', methods=['GET'])
@tokenRequired
def getOrder(_, newAccessToken):
    if 'orderId' in request.args:
        orderId: str = request.args['orderId']
    else:
        return create400Response(message='bErrorFieldCheck', newAccessToken=newAccessToken)

    dbio = DatabaseIO()
    data = dbio.getOrder(orderId)

    if data is None:
        return create400Response(message='bDataNotFound', newAccessToken=newAccessToken)

    return create200ResponseData(body=data, newAccessToken=newAccessToken)


@ordersApi.route('/deleteOrder', methods=['POST'])
@tokenRequired
def deleteOrder(_, newAccessToken):
    orderId: str = request.json.get('orderId')
    if orderId is None:
        return create400Response(message='bErrorFieldCheck', newAccessToken=newAccessToken)

    dbio = DatabaseIO()
    data = dbio.getOrder(orderId)
    hasDeleted = dbio.deleteOrder(orderId)

    if hasDeleted:
        return create200ResponseData(body={'message': 'bSuccessOrderDelete', 'order': data}, newAccessToken=newAccessToken)
    else:
        return create400Response(message='bErrorOrderDelete', newAccessToken=newAccessToken)


@ordersApi.route('/myOrders', methods=['GET'])
@tokenRequired
def myOrders(staff, newAccessToken):
    dbio = DatabaseIO()
    data = dbio.getMyOrders(staff['staffId'])

    return create200ResponseData(body=data, newAccessToken=newAccessToken)


@ordersApi.route('/openOrders', methods=['GET'])
@tokenRequired
def openOrders(_, newAccessToken):
    dbio = DatabaseIO()
    data = dbio.getOpenOrders()

    return create200ResponseData(body=data, newAccessToken=newAccessToken)


@ordersApi.route('/completeOrderItem', methods=['POST'])
@tokenRequired
def completeOrderItem(_, newAccessToken):
    orderId: str = request.json.get('orderId')
    itemId: str = request.json.get('itemId')
    increaseCompleted: bool = request.json.get('increaseCompleted')
    amount: int = request.json.get('amount')
    if orderId is None or itemId is None or increaseCompleted is None or amount is None:
        return create400Response(message='bErrorFieldCheck', newAccessToken=newAccessToken)

    dbio = DatabaseIO()
    hasUpdated = dbio.updateCompletedItems(orderId, itemId, increaseCompleted, amount)

    isCompleted = dbio.checkIfOrderComplete(orderId)
    dbio.completeOrder(orderId, isCompleted)

    if hasUpdated:
        return create200Response(message='bSuccessOrderUpdate', newAccessToken=newAccessToken)
    else:
        return create400Response(message='bErrorOrderUpdate', newAccessToken=newAccessToken)
