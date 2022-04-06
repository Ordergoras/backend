from datetime import datetime
from typing import Dict
from flask import Blueprint, request
from src.database.DatabaseIO import DatabaseIO
from src.utils.authUtils import generateUuid, tokenRequired, validateUserInput
from src.utils.responseUtils import create400Response, create200Response, create200ResponseData

ordersApi = Blueprint('ordersApi', __name__)


@ordersApi.route('/postOrder', methods=['POST'])
@tokenRequired
def addNewOrder(_, newAccessToken):
    tableNr: int = request.json.get('tableNr')
    staffId: str = request.json.get('staffId')
    orderedItems: Dict[str, int] = request.json.get('orderedItems')
    if tableNr is None or staffId is None or orderedItems is None:
        return create400Response(message='bErrorFieldCheck', newAccessToken=newAccessToken)
    elif not validateUserInput('orders', tableNr=tableNr, staffId=staffId, orderedItems=orderedItems):
        return create400Response(message='bErrorFieldInvalid')

    orderId = generateUuid()
    timestamp = datetime.now().timestamp()

    dbio = DatabaseIO()
    hasInserted = dbio.insertOrderData(orderId, tableNr, staffId, orderedItems, timestamp)

    if hasInserted:
        return create200Response(message='bSuccessOrderInsert', newAccessToken=newAccessToken)
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

    return create200ResponseData(body=data, newAccessToken=newAccessToken)
