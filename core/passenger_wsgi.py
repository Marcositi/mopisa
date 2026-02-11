import os
import sys

# Ruta a la carpeta de tu proyecto
sys.path.insert(0, os.path.dirname(__file__))

# Configura tu archivo settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'nombre_de_tu_proyecto.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()