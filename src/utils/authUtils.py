import os
from functools import wraps
from hashlib import pbkdf2_hmac
from typing import Dict
from uuid import uuid4
from flask import request, Response
import jwt
import base64
import json
from datetime import datetime, timedelta
from src.database.DatabaseIO import DatabaseIO
from src.utils.responseUtils import create401Response, create400Response
from src.utils.globals import ACCESS_TOKEN_LIFETIME, SESSION_TOKEN_LIFETIME


def validateUserInput(input_type: str, **kwargs) -> bool:
    if input_type == 'auth':
        if len(kwargs['name']) <= 255 and len(kwargs['password']) <= 255:
            return True
        else:
            return False


def generateUuid() -> str:
    return uuid4().hex


def generateSalt() -> str:
    salt = os.urandom(16)
    return salt.hex()


def generateHash(password: str, salt: str) -> str:
    password_hash = pbkdf2_hmac(
        'sha256',
        b"%b" % bytes(password, 'utf-8'),
        b"%b" % bytes(salt, 'utf-8'),
        10000,
    )
    return password_hash.hex()


def generateJwtToken(content: Dict, lifetime: int) -> str:
    dt = (datetime.now() + timedelta(seconds=lifetime)).timestamp()
    content['exp'] = dt
    token = jwt.encode(content, os.getenv('jwtSecretKey'), algorithm='HS256')
    return token


def decodeJwtToken(token: str) -> Dict[str, str] | Response | None:
    try:
        decodedToken = jwt.decode(token, os.getenv('jwtSecretKey'), algorithms='HS256', options={'require_exp': True})
    except jwt.ExpiredSignatureError as error:
        print('authUtils.decodeJwtToken.1', error)
        return None
    except jwt.InvalidTokenError as error:
        print('authUtils.decodeJwtToken.2', error)
        return create400Response('Token is invalid')

    return decodedToken


def decodePayloadWithoutExpiration(token: str) -> Dict | None:
    try:
        decodedToken = jwt.decode(token, os.getenv('jwtSecretKey'), algorithms='HS256', options={'verify_exp': False})
    except jwt.InvalidTokenError as error:
        print('authUtils.decodePayloadWithoutExpiration.2', error)
        return None

    return decodedToken


def createNewUserSession(sessionId: str, staffId: str) -> None:
    dbio = DatabaseIO()
    dbio.insertNewSession(sessionId, staffId)


def validateSession(sessionId: str) -> bool:
    dbio = DatabaseIO()
    session = dbio.getSession(sessionId)
    return session['isValid']


def validateUser(name: str, password: str) -> Dict[str, str] | None:
    dbio = DatabaseIO()
    currentUser = dbio.getAccountByNameWithAuthData(name)

    if currentUser:
        savedHash = currentUser['password']
        salt = currentUser['salt']
        passwordHash = generateHash(password, salt)
        sessionId = generateUuid()

        if passwordHash == savedHash:
            staffId = currentUser['staffId']
            accessToken = generateJwtToken({'staffId': staffId, 'sessionId': sessionId}, ACCESS_TOKEN_LIFETIME)
            sessionToken = generateJwtToken({'sessionId': sessionId}, SESSION_TOKEN_LIFETIME)
            createNewUserSession(sessionId, staffId)
            return {'accessToken': accessToken, 'sessionToken': sessionToken}
        else:
            return None

    else:
        return None


def checkCredentials(adminMode: bool) -> Response | Dict:
    accessToken = None
    sessionToken = None
    newAccessToken = None
    if 'accessToken' in request.cookies:
        accessToken = request.cookies['accessToken']
    if 'sessionToken' in request.cookies:
        sessionToken = request.cookies['sessionToken']

    if not accessToken or not sessionToken:
        return create401Response('Credential missing. PLease log in')

    oldAccessPayloadOrResponse = decodeJwtToken(accessToken)

    # staffId is None if token is expired
    if oldAccessPayloadOrResponse is None:
        accessPayload = decodePayloadWithoutExpiration(accessToken)
        sessionPayload = decodeJwtToken(sessionToken)
        if not accessPayload or not sessionPayload:
            return create401Response('Credential missing. PLease log in')
        if accessPayload['sessionId'] != sessionPayload['sessionId']:
            create400Response('Invalid credentials')
        dbio = DatabaseIO()
        session = dbio.getSession(sessionPayload['sessionId'])
        if not session['isValid']:
            create401Response('Session expired')
        if accessPayload['staffId'] != session['staffId']:
            create400Response('Invalid session')
        newAccessToken = generateJwtToken({'staffId': session['staffId'], 'sessionId': sessionPayload['sessionId']}, ACCESS_TOKEN_LIFETIME)
        staffId = session['staffId']
    # staffId is a response if token is invalid
    elif isinstance(oldAccessPayloadOrResponse, Response):
        return oldAccessPayloadOrResponse
    else:
        staffId = oldAccessPayloadOrResponse['staffId']

    dbio = DatabaseIO()
    staff = dbio.getAccountById(staffId)

    if adminMode and not staff['isAdmin']:
        return create401Response('Not authorized to perform this action.')

    print('newAccessToken', newAccessToken)

    return {'staff': staff, 'newAccessToken': newAccessToken}


def tokenRequired(f):
    @wraps(f)
    def decorator():
        creds = checkCredentials(False)

        if isinstance(creds, Response):
            return creds

        return f(creds['staff'], creds['newAccessToken'])

    return decorator


def adminRequired(f):
    @wraps(f)
    def decorator():
        creds = checkCredentials(True)

        if isinstance(creds, Response):
            return creds

        return f(creds['staff'], creds['newAccessToken'])

    return decorator
