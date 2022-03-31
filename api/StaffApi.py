from flask import Blueprint, request, jsonify
from database.DatabaseIO import DatabaseIO

staffApi = Blueprint('staffApi', __name__)


@staffApi.route('/registerStaff', methods=['GET', 'POST'])
def registerStaff():
    if 'name' in request.args and 'password' in request.args:
        name = request.args['name']
        password = request.args['password']
    else:
        return "Error: No name or password field provided. Please specify all necessary fields."

    dbio = DatabaseIO()
    rowId = dbio.insertNewAccount((name, password))
    data = dbio.getAccount(rowId)

    return jsonify(data)


@staffApi.route('/getStaff', methods=['GET'])
def getStaff():
    if 'staffId' in request.args:
        staffId = int(request.args['staffId'])
    else:
        return "Error: No staffId field provided. Please specify all necessary fields."

    dbio = DatabaseIO()
    data = dbio.getAccount(staffId)

    return jsonify(data)


@staffApi.route('/setAdmin', methods=['GET', 'POST'])
def setAdminStatus():
    if 'executingStaffId' in request.args and 'staffId' in request.args and 'newStatus' in request.args:
        executingStaffId = int(request.args['executingStaffId'])
        staffId = int(request.args['staffId'])
        newStatus = True if request.args['newStatus'] == 'True' else False
    else:
        return "Error: No executingStaffId, staffId or newStatus field provided. Please specify all necessary fields."

    dbio = DatabaseIO()
    data = dbio.setAdminStatus(executingStaffId, staffId, newStatus)

    return jsonify(data)
