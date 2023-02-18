from typing import List, Dict
from flask import Blueprint, request
from database.DatabaseIO import DatabaseIO
from utils.authUtils import generateUuid, tokenRequired, adminRequired, validateUserInput
from utils.responseUtils import create400Response, create200ResponseData
from utils.types import ItemGroup

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
    inStock: bool = request.json.get('inStock')
    group: ItemGroup = request.json.get('group')
    price: float = request.json.get('price')
    information: Dict[str, str] = request.json.get('information')

    if name is None or inStock is None or group is None or price is None:
        return create400Response(message='bErrorFieldCheck', newAccessToken=newAccessToken)
    elif not validateUserInput('storage', name=name, inStock=inStock, group=group, price=price):
        return create400Response(message='bErrorFieldInvalid')

    itemId = generateUuid()

    dbio = DatabaseIO()
    hasInserted = dbio.insertStorageData(itemId, name, inStock, group, price, information)

    if hasInserted:
        return create200ResponseData(body={'message': 'bSuccessItemInsert', 'args': {'name': name}}, newAccessToken=newAccessToken)
    else:
        return create400Response(message='bErrorItemInsert', newAccessToken=newAccessToken)


@storageApi.route('/updateItem', methods=['POST'])
@adminRequired
def updateItem(_, newAccessToken):
    itemId: str = request.json.get('itemId')
    name: str = request.json.get('name')
    inStock: bool = request.json.get('inStock')
    group: ItemGroup = request.json.get('group')
    price: float = request.json.get('price')
    information: Dict[str, str] = request.json.get('information')

    if itemId is None or name is None or inStock is None or group is None or price is None:
        return create400Response(message='bErrorFieldCheck', newAccessToken=newAccessToken)
    elif not validateUserInput('storage', name=name, inStock=inStock, group=group, price=price):
        return create400Response(message='bErrorFieldInvalid')

    dbio = DatabaseIO()
    hasUpdated = dbio.updateStorageData(itemId, name, inStock, group, price, information)

    if hasUpdated:
        return create200ResponseData(body={'message': 'bSuccessItemUpdate', 'args': {'name': name}}, newAccessToken=newAccessToken)
    else:
        return create400Response(message='bErrorItemUpdate', newAccessToken=newAccessToken)


@storageApi.route('/deleteItem', methods=['POST'])
@tokenRequired
def deleteItem(_, newAccessToken):
    itemId: str = request.json.get('itemId')
    if itemId is None:
        return create400Response(message='bErrorFieldCheck', newAccessToken=newAccessToken)

    dbio = DatabaseIO()
    name = dbio.getStorageItemData([itemId])[0]['name']
    hasDeleted = dbio.deleteItem(itemId)

    if hasDeleted:
        return create200ResponseData(body={'message': 'bSuccessItemDelete', 'args': {'name': name}}, newAccessToken=newAccessToken)
    else:
        return create400Response(message='bErrorItemDelete', newAccessToken=newAccessToken)
