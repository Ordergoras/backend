from flask import Blueprint, request, jsonify
from src.database.DatabaseIO import DatabaseIO
from src.utils.authUtils import validateUserInput, generateSalt, generateHash, validateUser, tokenRequired, adminRequired, generateUuid
from src.utils.responseUtils import create400Response, create401Response, create409Response, create200Response

staffApi = Blueprint('staffApi', __name__)


@staffApi.route('/registerStaff', methods=['POST'])
def registerStaff():
    name = request.json.get('name')
    password = request.json.get('password')
    if name is None or password is None:
        return create400Response('No name or password field provided. Please specify all necessary fields.')

    if not validateUserInput('auth', name=name, password=password):
        return create400Response('Enter a valid name and password.')

    salt = generateSalt()
    passHash = generateHash(password, salt)
    staffId = generateUuid()

    dbio = DatabaseIO()
    hasInserted = dbio.insertNewAccount(staffId, name, passHash, salt)

    if not hasInserted:
        return create409Response('Name already used')

    data = dbio.getAccountById(staffId)

    return jsonify(data)


@staffApi.route('/getStaff', methods=['GET'])
def getStaff():
    if 'staffId' in request.args:
        staffId = request.args['staffId']
    else:
        return create400Response('No staffId field provided. Please specify all necessary fields.')

    dbio = DatabaseIO()
    data = dbio.getAccountById(staffId)

    return jsonify(data)


@staffApi.route('/setAdmin', methods=['POST'])
@adminRequired
def setAdminStatus(__):
    staffId = request.json.get('staffId')
    newStatus = request.json.get('newStatus')

    if staffId is None or newStatus is None:
        return create400Response('No staffId or newStatus field provided. Please specify all necessary fields.')

    dbio = DatabaseIO()
    data = dbio.setAdminStatus(staffId, newStatus)

    return jsonify(data)


@staffApi.route('/login', methods=['POST'])
def login():
    name = request.json.get('name')
    password = request.json.get('password')

    if name is None or password is None:
        return create400Response('No name or password field provided. Please specify all necessary fields.')

    userToken = validateUser(name, password)

    if userToken:
        return jsonify({'jwtToken': userToken, 'name': name})
    else:
        return create401Response('Entered credentials are invalid')


@staffApi.route('/logout', methods=['POST'])
@tokenRequired
def logout(staff):
    return create200Response('Successfully logged out user {name}'.format(name=staff['name']))
