from django.utils.timezone import now

import logging
logger = logging.getLogger('logstash')


class LoggingMixin(object):

    def update_logger_extras(self, dic):
        self.__logger_extras.update(dic)

    """Mixin to log requests"""
    def initial(self, request, *args, **kwargs):

        self.__logging_dict = {}
        self.__logger_extras = {}

        self.__logging_dict.update({'time.start': now()})

        metas_allowed = [
            "REMOTE_ADDR",
            "REQUEST_SCHEME",
            "HTTP_ACCEPT_LANGUAGE",
            "HTTP_X_REQUESTED_WITH",
            "HTTP_USER_AGENT",
            "HTTP_ACCEPT",
            "HTTP_COOKIE",
            "HTTP_REFERER",
            "SERVER_PROTOCOL"
        ]
        for k, v in request.META.iteritems():
            if k in metas_allowed:
                self.__logging_dict.update({'meta.{}'.format(k): v})

        for k, v in request.query_params.iteritems():
            self.__logging_dict.update({'param.{}'.format(k): v})

        # regular intitial, including auth check
        super(LoggingMixin, self).initial(request, *args, **kwargs)

        # add user to log after auth
        user = request.user
        if user.is_anonymous():
            user = None
        else:
            user = user.username

        self.__logging_dict.update({'user': user})

    def finalize_response(self, request, response, *args, **kwargs):
        # regular finalize response
        response = super(LoggingMixin, self).finalize_response(request, response, *args, **kwargs)

        # add logger extras
        for k, v in self.__logger_extras.iteritems():
            self.__logging_dict.update({'parsed.{}'.format(k): v})

        # compute response time
        self.__logging_dict['time.end'] = now()
        response_timedelta = self.__logging_dict['time.end'] - self.__logging_dict['time.start']
        response_ms = int(response_timedelta.total_seconds() * 1000)

        # save to log
        self.__logging_dict['status_code'] = response.status_code
        self.__logging_dict['time.elapsed'] = response_ms

        # send log
        logger.info(request.path, extra=self.__logging_dict)

        # return
        return response
