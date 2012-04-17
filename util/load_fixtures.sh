#!/bin/bash

python manage.py loaddata apps/usuarios/fixtures/usuario.json

#python manage.py loaddata apps/catastro/fixtures/provincia.json
python manage.py loaddata apps/core/fixtures/linea.json
python manage.py loaddata apps/core/fixtures/recorrido.json
#python manage.py loaddata apps/catastro/fixtures/ciudad.json
