from uwsgidecorators import *
import os
from django.core.management import call_command

@spool
def crear_thumbs(arguments):
    call_command('crear_thumbs', recorrido_id=arguments['recorrido_id'])
