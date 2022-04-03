import os
from functools import wraps
from hashlib import pbkdf2_hmac
from typing import Dict
from uuid import uuid4
from flask import request, Response
import jwt
from datetime import datetime, timedelta, timezone
from src.database.DatabaseIO import DatabaseIO
from src.utils.responseUtils import create401Response


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


def generateJwtToken(content: Dict) -> str:
    # TODO fix expiry date
    dt = datetime.now(timezone.utc) + timedelta(seconds=20)
    token = jwt.encode(content, os.getenv('jwtSecretKey'), algorithm='HS256', headers={'exp': dt.timestamp()})
    return token


def decodeJwtToken(token: str) -> str:
    staffId = jwt.decode(token, os.getenv('jwtSecretKey'), algorithms='HS256')['staffId']
    return staffId


def validateUser(name: str, password: str) -> str | None:
    dbio = DatabaseIO()
    currentUser = dbio.getAccountByNameWithAuthData(name)

    if currentUser:
        savedHash = currentUser['password']
        salt = currentUser['salt']
        passwordHash = generateHash(password, salt)

        if passwordHash == savedHash:
            staffId = currentUser['staffId']
            jwtToken = generateJwtToken({'staffId': staffId})
            return jwtToken
        else:
            return None

    else:
        return None


def validateToken(token: str) -> Dict | None:
    try:
        staffId = decodeJwtToken(token)
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError) as error:
        print('authUtils.validateToken', error)
        return None

    dbio = DatabaseIO()
    return dbio.getAccountById(staffId)


def checkAuthHeader(adminMode: bool) -> Response | dict:
    token = None
    if 'authorization' in request.headers:
        token = request.headers['authorization']

    if not token:
        return create401Response('Authorization header is missing.')

    staff = validateToken(token)

    if staff is None or (adminMode and not staff['isAdmin']):
        return create401Response('Token is invalid.')

    return staff


def tokenRequired(f):
    @wraps(f)
    def decorator():
        staff = checkAuthHeader(False)

        if not isinstance(staff, Dict):
            return staff

        return f(staff)

    return decorator


def adminRequired(f):
    @wraps(f)
    def decorator():
        staff = checkAuthHeader(True)

        if not isinstance(staff, Dict):
            return staff

        return f(staff)

    return decorator
