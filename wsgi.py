import os
import sys

sys.path.append('/home/jperelli/Escritorio/cualbondi/repo/')
sys.path.append('/home/jperelli/Escritorio/cualbondi/')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "repo.settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
