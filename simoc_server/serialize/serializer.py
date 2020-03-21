import json
import datetime
import pytimeparse

from json.decoder import JSONDecodeError
from abc import ABCMeta, abstractmethod
from flask import make_response
from simoc_server import app

_serializer = None


def decode_msgpack(obj):
    if b'__datetime__' in obj:
        obj = datetime.datetime.strptime(obj["as_str"], "%Y%m%dT%H:%M:%S.%f")
    if b'__timedelta__' in obj:
        seconds = datetime.timedelta(pytimeparse.parse(obj['as_str']))
    return obj


def encode_msgpack(obj):
    if isinstance(obj, datetime.datetime):
        return {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f")}
    if isinstance(obj, datetime.timedelta):
        return {'__timedelta__':True, 'as_str': str(obj)}
    return obj


class Serializer(object):
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def serialize_response(cls, obj):
        pass

    @classmethod
    @abstractmethod
    def deserialize_request(cls, request):
        pass

    @classmethod
    @abstractmethod
    def get_format_name(cls):
        pass


class JsonSerializer(Serializer):

    @classmethod
    def serialize_response(cls, obj):
        resp = make_response(json.dumps(obj))
        resp.headers["Content-Type"] = "application/json; charset=utf-8"
        return resp

    @classmethod
    def deserialize_request(cls, request):
        request.__dict__["deserialized"] = None

        data = request.get_data()
        if data:
            try:
                request.__dict__["deserialized"] = json.loads(data)
            except JSONDecodeError:
                app.logger.error("Error deserializing json: {}".format(data))

    @classmethod
    def get_format_name(cls):
        return "json"


def serialize_response(obj):
    return _serializer.serialize_response(obj)


def deserialize_request(request):
    return _serializer.deserialize_request(request)


def data_format_name():
    return _serializer.get_format_name()


def set_serializer(serializer):
    global _serializer
    _serializer = serializer
    app.logger.info("Using serializer: {}".format(_serializer.__class__.__name__))


def init_serializer():
    global _serializer
    if "SERIALIZER" in app.config:
        _serializer = app.config["SERIALIZER"]
    else:
        _serializer = JsonSerializer()


init_serializer()
