import msgpack
import flask.json
from json.decoder import JSONDecodeError
from abc import ABCMeta, abstractmethod
from flask import make_response
import traceback
class Serializer(object):
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def serialize_to_string(obj):
        pass

    @classmethod
    @abstractmethod
    def deserialize_request(request):
        pass

class JsonSerializer(Serializer):

    @classmethod
    def serialize_response(cls, obj):
        return make_response(flask.json.dumps(obj))

    @classmethod
    def deserialize_request(cls, request):
        try:
            request.__dict__["deserialized"] = flask.json.loads(request.get_data())
        except JSONDecodeError:
            request.__dict__["deserialized"] = None


class MsgPackSerializer(Serializer):

    @classmethod
    def serialize_response(cls, obj):
        a = make_response(msgpack.packb(obj))
        return a

    @classmethod
    def deserialize_request(cls, request):
        data = request.get_data()
        if data:
            request.__dict__["deserialized"] = msgpack.unpackb(data, encoding='utf-8')


_serializer = MsgPackSerializer()

serialize_response = _serializer.serialize_response
deserialize_request = _serializer.deserialize_request
