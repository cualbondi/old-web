import time

import pymongo
from django.db import connection
from django.utils.encoding import smart_str

from settings import REQUEST_LOGGING_BACKEND


class MongoDBLogger(object):

    def __init__(self):
        self.conn = pymongo.Connection(
            "{0}:{1}".format(
                REQUEST_LOGGING_BACKEND['host'],
                REQUEST_LOGGING_BACKEND['port']
            )
        )
        self.db = self.conn[REQUEST_LOGGING_BACKEND['db']]
        self.collection = self.db[REQUEST_LOGGING_BACKEND['collection']]
        self.filters = ['/api']

    def log_request_info(self, info, request):
        for _filter in self.filters:
            if not request.path_info.startswith(_filter):
                return

        self.collection.insert(info)


class APIRequestLoggingMiddleware(object):

    def __init__(self):
        self.logger = MongoDBLogger()

    def process_request(self, request):
        request._start = time.time()

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_response(self, request, response):
        try:
            info = {
                'timestamp': request._start,
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
            self.logger.log_request_info(info, request)
        except Exception as e:
            # TODO: Mandar estos mensajes de error a archivos de LOG.
            print "Got error while logging request info: {0}".format(e)

        return response