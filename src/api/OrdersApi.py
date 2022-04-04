from datetime import datetime
from typing import Dict
from flask import Blueprint, request, jsonify
from src.database.DatabaseIO import DatabaseIO
from src.utils.authUtils import generateUuid
from src.utils.responseUtils import create400Response, create200Response

ordersApi = Blueprint('ordersApi', __name__)


@ordersApi.route('/postOrder', methods=['POST'])
def addNewOrder():
    tableNr: int = request.json.get('tableNr')
    staffId: str = request.json.get('staffId')
    orderedItems: Dict[str, int] = request.json.get('orderedItems')
    if tableNr is None or staffId is None or orderedItems is None:
        return create400Response('No tableNr, staffId or orderedItems field provided. Please specify all necessary fields.')

    orderId = generateUuid()
    timestamp = datetime.now().timestamp()

    dbio = DatabaseIO()
    hasInserted = dbio.insertOrderData(orderId, tableNr, staffId, orderedItems, timestamp)

    if hasInserted:
        return create200Response('Created order {orderId}'.format(orderId=orderId))
    else:
        return create400Response('Couldn\'t insert order')


@ordersApi.route('/getOrder', methods=['GET'])
def getOrder():
    if 'orderId' in request.args:
        orderId: str = request.args['orderId']
    else:
        return create400Response('No orderId field provided. Please specify all necessary fields.')

    dbio = DatabaseIO()
    data = dbio.getOrder(orderId)

    return jsonify(data)
