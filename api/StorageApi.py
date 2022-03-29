from flask import Blueprint, request, jsonify
from database.DatabaseIO import DatabaseIO

storageApi = Blueprint('storageApi', __name__)


@storageApi.route('/getItems', methods=['GET'])
def getItems():
    if 'itemIds' in request.args:
        itemIdsString = request.args['itemIds']
        itemIds = list(int(value) for value in itemIdsString.split(','))
    else:
        return "Error: No itemIds field provided. Please specify all necessary fields."

    dbio = DatabaseIO()
    data = dbio.getStorageItemData(itemIds)
    return jsonify(data)


@storageApi.route('/getAllItems', methods=['GET'])
def getAllItems():
    dbio = DatabaseIO()
    data = dbio.getStorageFullData()
    return jsonify(data)


@storageApi.route('/postItem', methods=['GET', 'POST'])
def addNewItem():
    if 'name' in request.args and 'amount' in request.args:
        name = request.args['name']
        amount = int(request.args['amount'])
    else:
        return "Error: No name or amount field provided. Please specify all necessary fields."

    dbio = DatabaseIO()
    dbio.insertStorageData((name, amount))

    return jsonify('Inserted {name} with {amount} units'.format(name=name, amount=amount))


@storageApi.route('/updateItemAmount', methods=['GET', 'POST'])
def updateItemAmount():
    if 'itemId' in request.args and 'amount' in request.args:
        itemId = int(request.args['itemId'])
        amount = int(request.args['amount'])
    else:
        return "Error: No itemId or amount field provided. Please specify all necessary fields."

    dbio = DatabaseIO()
    dbio.updateStorageData((itemId, amount))
    data = dbio.getStorageItemData([itemId])

    return jsonify(data)


@storageApi.route('/retrieveItems', methods=['GET', 'POST'])
def retrieveItems():
    """
    pathVariable 'itemIds' - list of integers seperated by ',', e.g. itemIds=1,2,3

    pathVariable 'amounts' - list of integers seperated by ',', e.g. amounts=4,11,7

    requires both lists to be of equal length

    takes away each amount from the corresponding id in storage (as long as enough items are stored)

    :return: json of dictionary containing all modified tuples
    """
    if 'itemIds' in request.args and 'amounts' in request.args:
        itemIdsString = request.args['itemIds']
        amountsString = request.args['amounts']
        itemIds = list(int(value) for value in itemIdsString.split(','))
        amounts = list(int(value) for value in amountsString.split(','))
    else:
        return "Error: No itemIds or amounts provided. Please specify all necessary fields."

    dbio = DatabaseIO()
    dbio.retrieveItemFromStorage(list(zip(itemIds, amounts)))
    data = dbio.getStorageItemData(itemIds)

    return jsonify(data)
