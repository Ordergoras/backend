import json
from flask import Response


def create400Response(message: str) -> Response:
    return Response(json.dumps({'message': message}), status=400)


def create401Response(message: str) -> Response:
    return Response(json.dumps({'message': message}), status=401)


def create409Response(message: str) -> Response:
    return Response(json.dumps({'message': message}), status=409)
