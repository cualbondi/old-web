import os
from django.core.management import call_command

# workaround for testing purposes
# from http://lists.unbit.it/pipermail/uwsgi/2012-May/004196.html
try:
    from uwsgidecorators import spool
except ImportError:
    def spool(f):
        f.spool = f
        return f


@spool
def crear_thumbs(arguments):
    call_command('crear_thumbs', recorrido_id=arguments['recorrido_id'])
