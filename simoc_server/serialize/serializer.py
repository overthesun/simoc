import msgpack
import flask.json
import traceback
from msgpack.exceptions import ExtraData, UnpackException
from json.decoder import JSONDecodeError
from abc import ABCMeta, abstractmethod
from flask import make_response
from simoc_server import app

_serializer = None

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
        resp = make_response(flask.json.dumps(obj))
        resp.mimetype = "application/json"
        return resp

    @classmethod
    def deserialize_request(cls, request):
        request.__dict__["deserialized"] = None

        data = request.get_data()
        if data:
            try:
                request.__dict__["deserialized"] = flask.json.loads(data)
            except JSONDecodeError:
                app.logger.error("Error deserializing json: {}".format(data))

    @classmethod
    def get_format_name(cls):
        return "json"

class MsgPackSerializer(Serializer):

    @classmethod
    def serialize_response(cls, obj):
        resp = make_response(msgpack.packb(obj))
        resp.mimetype = "application/x-msgpack"
        return resp

    @classmethod
    def deserialize_request(cls, request):
        request.__dict__["deserialized"] = None

        data = request.get_data()
        if data:
            try:
                request.__dict__["deserialized"] = msgpack.unpackb(data, encoding='utf-8')
            except (UnpackException, ExtraData) as e:
                app.logger.error("Error deserializing msgpack: {}".format(data))

    @classmethod
    def get_format_name(cls):
        return "msgpack"

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
        _serializer = MsgPackSerializer()

init_serializer()