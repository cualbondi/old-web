import json
import time
from datetime import datetime

import pymongo
from elasticsearch import Elasticsearch
from django.db import connection
from django.utils.encoding import smart_str

from settings import REQUEST_LOGGING_BACKEND

ES_CONNECTION = Elasticsearch(REQUEST_LOGGING_BACKEND['host'])

class ElasticsearchLogger(object):

    @classmethod
    def save_document(cls, info):
        ES_CONNECTION.index(index=REQUEST_LOGGING_BACKEND['index'],
                            doc_type=REQUEST_LOGGING_BACKEND['type'],
                            body=info, timeout=1)


class MongoDBLogger(object):
    _connection = None

    @classmethod
    def get_mongodb_connection(cls):
        if cls._connection is not None:
            return cls._connection
        try:
            cls._connection = pymongo.Connection(
                "{0}:{1}".format(
                    REQUEST_LOGGING_BACKEND['host'],
                    REQUEST_LOGGING_BACKEND['port']
                )
            )
            return cls._connection
        except Exception as e:
            # TODO: Add log here.
            return None

    @classmethod
    def save_document(cls, collection, document):
        connection = cls.get_mongodb_connection()
        if connection is None:
            return
        db = connection[REQUEST_LOGGING_BACKEND['db']]
        collection = db[collection]
        collection.insert(document)


class APIRequestLoggingMiddleware(object):

    def __init__(self):
        self.filters = ['/api']

    def buid_function_name(self, request):
        """ Transforma la URL de la request en el nombre de una funcion
            reemplazando las "/" por "_".
            Por ejemplo: "/api/recorridos" => "get_api_recorridos_info"
        """
        return "get{0}info".format(request.path.replace('/', '_'))

    def get_json_content(self, request, response):
        """ Si la request es JSONP, el response content viene wrappeado
            en una callback. para poder parsear el content como JSON, es
            necesario eliminar la callback del string.
        """
        content = response.content
        if ("callback" in request.GET and "_" in request.GET):
            # is JSONP request, remove callback from content
            callback = request.GET.dict()["callback"]
            content = content.replace(callback + "(", "")[:-1]
        return json.loads(content)

    def get_generic_info(self, request, response):
        return {
            'timestamp': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            'method': request.method,
            'duration_in_seconds': time.time() - request._start,
            'code': response.status_code,
            'url': smart_str(request.path_info),
            'full_url': smart_str(request.get_full_path()),
            'ip': request.META.get('REMOTE_ADDR'),
            'get_params': request.GET.dict(),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'query_count': len(connection.queries),
        }

    def get_api_catastro_info(self, json_content):
        return {'cant_resultados': len(json_content)}

    def get_api_recorridos_info(self, json_content):
        return {
            'cant_resultados': json_content.get('cant'),
            'cached': json_content.get('cached')
        }

    def process_request(self, request):
        request._start = time.time()

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_response(self, request, response):
        for _filter in self.filters:
            if not request.path_info.startswith(_filter):
                return response

        try:
            info = self.get_generic_info(request, response)

            function_name = self.buid_function_name(request)
            if hasattr(self, function_name):
                json_content = self.get_json_content(request, response)
                info.update(getattr(self, function_name)(json_content))

            ElasticsearchLogger.save_document(info)
        except Exception:
            # TODO: Add log here.
            pass

        return response
