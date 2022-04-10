import json
from typing import Dict, List
from flask import Response, jsonify
from src.utils.globals import ACCESS_TOKEN_LIFETIME


def create200Response(message: str, newAccessToken: str = None) -> Response:
    response = Response(json.dumps({'message': message}), status=200)
    if newAccessToken is not None:
        response.set_cookie('accessToken', newAccessToken, max_age=ACCESS_TOKEN_LIFETIME, httponly=True)
    return response


def create200ResponseData(body: Dict | List, newAccessToken: str = None) -> Response:
    response = jsonify(body)
    if newAccessToken is not None:
        response.set_cookie('accessToken', newAccessToken, max_age=ACCESS_TOKEN_LIFETIME, httponly=True)
    return response


def create400Response(message: str, newAccessToken: str = None) -> Response:
    response = Response(json.dumps({'message': message}), status=400)
    if newAccessToken is not None:
        response.set_cookie('accessToken', newAccessToken, max_age=ACCESS_TOKEN_LIFETIME, httponly=True)
    return response


def create401Response(message: str, newAccessToken: str = None) -> Response:
    response = Response(json.dumps({'message': message}), status=401)
    if newAccessToken is not None:
        response.set_cookie('accessToken', newAccessToken, max_age=ACCESS_TOKEN_LIFETIME, httponly=True)
    return response


def create409Response(message: str, newAccessToken: str = None) -> Response:
    response = Response(json.dumps({'message': message}), status=409)
    if newAccessToken is not None:
        response.set_cookie('accessToken', newAccessToken, max_age=ACCESS_TOKEN_LIFETIME, httponly=True)
    return response
