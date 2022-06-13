from flask import Blueprint, request, jsonify
from src.database.DatabaseIO import DatabaseIO
from src.utils.authUtils import validateUserInput, generateSalt, generateHash, validateUser, adminRequired, generateUuid, decodeJwtToken, \
    tokenRequired
from src.utils.responseUtils import create400Response, create401Response, create409Response, create200Response, create200ResponseData
from src.utils.globals import ACCESS_TOKEN_LIFETIME, SESSION_TOKEN_LIFETIME, COOKIE_OPTIONS

staffApi = Blueprint('staffApi', __name__)


@staffApi.route('/registerStaff', methods=['POST'])
def registerStaff():
    name: str = request.json.get('name')
    password: str = request.json.get('password')

    if name is None or password is None:
        return create400Response(message='bErrorFieldCheck')
    elif not validateUserInput('staff', name=name, password=password):
        return create400Response(message='errorCredInvalid')

    salt = generateSalt()
    passHash = generateHash(password, salt)
    staffId = generateUuid()

    dbio = DatabaseIO()
    hasInserted = dbio.insertNewAccount(staffId, name, passHash, salt)

    if not hasInserted:
        return create409Response(message='bErrorDupName')

    data = validateUser(name, password)

    response = jsonify({'staffId': staffId, 'name': name, 'isAdmin': False})
    response.set_cookie('accessToken', data['accessToken'], max_age=ACCESS_TOKEN_LIFETIME, **COOKIE_OPTIONS)
    response.set_cookie('sessionToken', data['sessionToken'], max_age=SESSION_TOKEN_LIFETIME, **COOKIE_OPTIONS)
    return response


@staffApi.route('/getStaff', methods=['GET'])
@adminRequired
def getStaff(_, newAccessToken):
    if 'staffId' in request.args:
        staffId: str = request.args['staffId']
    else:
        return create400Response(message='bErrorFieldCheck', newAccessToken=newAccessToken)

    dbio = DatabaseIO()
    data = dbio.getAccountById(staffId)

    if data is None:
        return create400Response(message='bDataNotFound', newAccessToken=newAccessToken)

    return create200ResponseData(body=data, newAccessToken=newAccessToken)


@staffApi.route('/getFullStaff', methods=['GET'])
@adminRequired
def getFullStaff(_, newAccessToken):
    dbio = DatabaseIO()
    data = dbio.getAllAccounts()

    if data is None:
        return create400Response(message='bDataNotFound', newAccessToken=newAccessToken)

    return create200ResponseData(body=data, newAccessToken=newAccessToken)


@staffApi.route('/setAdmin', methods=['POST'])
@adminRequired
def setAdminStatus(_, newAccessToken):
    staffId: str = request.json.get('staffId')
    newStatus: bool = request.json.get('newStatus')

    if staffId is None or newStatus is None:
        return create400Response(message='bErrorFieldCheck', newAccessToken=newAccessToken)

    dbio = DatabaseIO()
    data = dbio.setAdminStatus(staffId, newStatus)

    if data is None:
        return create400Response(message='bDataNotFound', newAccessToken=newAccessToken)

    return create200ResponseData(body=data, newAccessToken=newAccessToken)


@staffApi.route('/login', methods=['POST'])
def login():
    name: str = request.json.get('name')
    password: str = request.json.get('password')

    if name is None or password is None:
        return create400Response(message='bErrorFieldCheck')
    elif not validateUserInput('staff', name=name, password=password):
        return create400Response(message='errorCredInvalid')

    data = validateUser(name, password)

    if data is not None:
        response = jsonify({'staffId': data['staffId'], 'name': name, 'isAdmin': data['isAdmin']})
        response.set_cookie('accessToken', data['accessToken'], max_age=ACCESS_TOKEN_LIFETIME, **COOKIE_OPTIONS)
        response.set_cookie('sessionToken', data['sessionToken'], max_age=SESSION_TOKEN_LIFETIME, **COOKIE_OPTIONS)
        return response
    else:
        return create401Response(message='bErrorCredInvalid')


@staffApi.route('/logout', methods=['POST'])
def logout():
    if 'sessionToken' in request.cookies:
        payload = decodeJwtToken(request.cookies['sessionToken'])
        if payload:
            dbio = DatabaseIO()
            dbio.deleteSession(payload['sessionId'])

    response = create200Response(message='bSuccessLogout')
    response.set_cookie('accessToken', '', expires=0, **COOKIE_OPTIONS)
    response.set_cookie('sessionToken', '', expires=0, **COOKIE_OPTIONS)
    return response


@staffApi.route('/verifyCred', methods=['GET'])
@tokenRequired
def verifyCred(staff, newAccessToken):
    return create200ResponseData(body=staff, newAccessToken=newAccessToken)
