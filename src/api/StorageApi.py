from typing import List, Dict
from flask import Blueprint, request
from src.database.DatabaseIO import DatabaseIO
from src.utils.authUtils import generateUuid, tokenRequired, adminRequired, validateUserInput
from src.utils.responseUtils import create400Response, create200ResponseData
from src.utils.types import ItemGroup

storageApi = Blueprint('storageApi', __name__)


@storageApi.route('/getItems', methods=['PUT'])
@tokenRequired
def getItems(_, newAccessToken):
    itemIds: List[str] = request.json.get('itemIds')
    if itemIds is None:
        return create400Response(message='bErrorFieldCheck', newAccessToken=newAccessToken)

    dbio = DatabaseIO()
    data = dbio.getStorageItemData(itemIds)

    if data is None:
        return create400Response(message='bDataNotFound', newAccessToken=newAccessToken)

    return create200ResponseData(body=data, newAccessToken=newAccessToken)


@storageApi.route('/getAllItems', methods=['GET'])
@tokenRequired
def getAllItems(_, newAccessToken):
    dbio = DatabaseIO()
    data = dbio.getStorageFullData()
    return create200ResponseData(body=data, newAccessToken=newAccessToken)


@storageApi.route('/postItem', methods=['POST'])
@adminRequired
def addNewItem(_, newAccessToken):
    name: str = request.json.get('name')
    amount: int = request.json.get('amount')
    group: ItemGroup = request.json.get('group')
    price: float = request.json.get('price')

    if name is None or amount is None or group is None:
        return create400Response(message='bErrorFieldCheck', newAccessToken=newAccessToken)
    elif not validateUserInput('storage', name=name, amount=amount, group=group):
        return create400Response(message='bErrorFieldInvalid')

    itemId = generateUuid()

    dbio = DatabaseIO()
    hasInserted = dbio.insertStorageData(itemId, name, amount, group, price)

    if hasInserted:
        return create200ResponseData(body={'message': 'bSuccessItemInsert', 'args': {'name': name, 'amount': amount}}, newAccessToken=newAccessToken)
    else:
        return create400Response(message='bErrorItemInsert', newAccessToken=newAccessToken)


@storageApi.route('/updateItem', methods=['POST'])
@adminRequired
def updateItem(_, newAccessToken):
    itemId: str = request.json.get('itemId')
    name: str = request.json.get('name')
    amount: int = request.json.get('amount')
    group: ItemGroup = request.json.get('group')
    price: float = request.json.get('price')
    if itemId is None or name is None or amount is None or group is None or price is None:
        return create400Response(message='bErrorFieldCheck', newAccessToken=newAccessToken)

    dbio = DatabaseIO()
    hasUpdated = dbio.updateStorageData(itemId, name, amount, group, price)

    if hasUpdated:
        return create200ResponseData(body={'message': 'bSuccessItemUpdate', 'args': {'name': name}}, newAccessToken=newAccessToken)
    else:
        return create400Response(message='bErrorItemUpdate', newAccessToken=newAccessToken)


@storageApi.route('/retrieveItems', methods=['POST'])
@tokenRequired
def retrieveItems(_, newAccessToken):
    retrievedItems: Dict[str, int] = request.json.get('retrievedItems')
    if retrievedItems is None:
        return create400Response(message='bErrorFieldCheck', newAccessToken=newAccessToken)

    dbio = DatabaseIO()
    dbio.retrieveItemsFromStorage(retrievedItems)
    data = dbio.getStorageItemData([key for key in retrievedItems])

    return create200ResponseData(body=data, newAccessToken=newAccessToken)
