from typing import List, Dict
from flask import Blueprint, request, jsonify
from src.database.DatabaseIO import DatabaseIO
from src.utils.authUtils import generateUuid
from src.utils.responseUtils import create400Response, create200Response
from src.utils.types import ItemGroup

storageApi = Blueprint('storageApi', __name__)


@storageApi.route('/getItems', methods=['PUT'])
def getItems():
    itemIds: List[str] = request.json.get('itemIds')
    if itemIds is None:
        return create400Response('No itemIds field provided. Please specify all necessary fields.')

    dbio = DatabaseIO()
    data = dbio.getStorageItemData(itemIds)
    return jsonify(data)


@storageApi.route('/getAllItems', methods=['GET'])
def getAllItems():
    dbio = DatabaseIO()
    data = dbio.getStorageFullData()
    return jsonify(data)


@storageApi.route('/postItem', methods=['POST'])
def addNewItem():
    name: str = request.json.get('name')
    amount: int = request.json.get('amount')
    group: ItemGroup = request.json.get('group')
    if name is None or amount is None or group is None:
        return create400Response('No name or amount field provided. Please specify all necessary fields.')

    itemId = generateUuid()

    dbio = DatabaseIO()
    hasInserted = dbio.insertStorageData(itemId, name, amount, group)

    if hasInserted:
        return create200Response('Inserted {name} with {amount} units'.format(name=name, amount=amount))
    else:
        return create400Response('Couldn\'t insert item')


@storageApi.route('/updateItemAmount', methods=['POST'])
def updateItemAmount():
    itemId: str = request.json.get('itemId')
    amount: int = request.json.get('amount')
    if itemId is None or amount is None:
        return create400Response('No itemId or amount field provided. Please specify all necessary fields.')

    dbio = DatabaseIO()
    dbio.updateStorageData(itemId, amount)
    data = dbio.getStorageItemData([itemId])

    return jsonify(data)


@storageApi.route('/retrieveItems', methods=['POST'])
def retrieveItems():
    retrievedItems: Dict[str, int] = request.json.get('retrievedItems')
    if retrievedItems is None:
        return create400Response('No retrievedItems field provided. Please specify all necessary fields.')

    dbio = DatabaseIO()
    dbio.retrieveItemsFromStorage(retrievedItems)
    data = dbio.getStorageItemData([key for key in retrievedItems])

    return jsonify(data)
