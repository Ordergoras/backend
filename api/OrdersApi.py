from flask import Blueprint, request, jsonify
from database.DatabaseIO import DatabaseIO

ordersApi = Blueprint('ordersApi', __name__)


@ordersApi.route('/postOrder', methods=['GET', 'POST'])
def addNewOrder():
    """
    example call: http://localhost:5000/orders/postOrder?tableNr=12&staffId=10&orderedItems=1,4;2,7;3,9
    :return:
    """
    if 'tableNr' in request.args and 'staffId' in request.args and 'orderedItems' in request.args:
        tableNr = int(request.args['tableNr'])
        staffId = int(request.args['staffId'])
        string = request.args['orderedItems']
        tupleStrings = string.split(';')
        orderedItems = []
        for tupleS in tupleStrings:
            values = tupleS.split(',')
            orderedItems.append((int(values[0]), int(values[1])))
    else:
        return "Error: No tableNr, staffId or orderedItems field provided. Please specify all necessary fields."

    dbio = DatabaseIO()
    rowId = dbio.insertOrderData((tableNr, staffId, orderedItems))
    data = dbio.getOrder(rowId)

    return jsonify(data)


@ordersApi.route('/getOrder', methods=['GET'])
def getOrder():
    if 'orderId' in request.args:
        orderId = int(request.args['orderId'])
    else:
        return "Error: No orderId field provided. Please specify all necessary fields."

    dbio = DatabaseIO()
    data = dbio.getOrder(orderId)

    return jsonify(data)
