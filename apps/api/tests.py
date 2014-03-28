# -*- coding: utf-8 -*-
# Copyright 2011-2012, Cualbondi
"""Tests para los API Handlers"""

import json
from copy import deepcopy

from django_webtest import WebTest

from apps.api.factories import CiudadFactory, RecorridoFactory
from apps.core.models import Posicion


class TestPosicionHandler(WebTest):
    def setUp(self):
        self.recorrido = RecorridoFactory()
        self.url = '/api/posicion/{0}/'.format(self.recorrido.id)
        self.data = {
            'lat': -34.8723,
            'lng': -57.2398,
            'uuid': '550e8400-e29b-41d4-a716-446655440000'
        }

    def test_cargar_posicion_correcta(self):
        """Debe crear un objeto posicion cuando el POST se realiza con datos correctos"""

        response = self.app.post(self.url, self.data)

        self.assertEqual(response.status, '200 OK')

        posicion = Posicion.objects.get(id=1)

        point = posicion.latlng
        self.assertEqual(point.y, self.data['lat'])
        self.assertEqual(point.x, self.data['lng'])

        self.assertEqual(posicion.dispositivo_uuid, self.data['uuid'])

        self.assertTrue(hasattr(posicion, "timestamp"))

    def test_cargar_posicion_recorrido_no_existe(self):
        """Debe devolver 404 y NO crear el objeto cuando el recorrido no existe"""

        url = '/api/posicion/999/'
        response = self.app.post(url, self.data, expect_errors=True)

        self.assertEqual(response.status, '404 NOT FOUND')

        self.assertEqual(Posicion.objects.count(), 0)

    def test_cargar_posicion_faltan_datos(self):
        """Debe devolver 400 y no crear el objeto cuando faltan datos en el POST"""

        data = deepcopy(self.data)
        del data['lat']

        response = self.app.post(self.url, data, expect_errors=True)
        self.assertEqual(response.status, '400 BAD REQUEST')

        data = deepcopy(self.data)
        del data['lng']

        response = self.app.post(self.url, data, expect_errors=True)
        self.assertEqual(response.status, '400 BAD REQUEST')

        self.assertEqual(Posicion.objects.count(), 0)

    def test_cargar_posicion_datos_incorrectos(self):
        """Debe devolver 400 y no crear el objeto cuando los datos son incorrectos"""

        data = deepcopy(self.data)
        data['lat'] = "bla"

        response = self.app.post(self.url, data, expect_errors=True)
        self.assertEqual(response.status, '400 BAD REQUEST')

        data = deepcopy(self.data)
        data['lng'] = "bla"

        response = self.app.post(self.url, data, expect_errors=True)
        self.assertEqual(response.status, '400 BAD REQUEST')

        self.assertEqual(Posicion.objects.count(), 0)


class TestCiudadHandler(WebTest):
    def setUp(self):
        for i in range(5):
            CiudadFactory()

    def test_ciudades_listado(self):
        """Debe devolver el listado de ciudades cuando no se le pasa ningun ID de ciudad como parametro"""
        response = self.app.get('/api/ciudades/')
        self.assertEqual(response.status, '200 OK')
        data = json.loads(response.content)
        self.assertTrue(type(data), list)
        self.assertEqual(len(data), 5)
        for ciudad in data:
            for field in ['nombre', 'slug', 'provincia', 'activa', 'centro',
                          'descripcion', 'poligono']:
                self.assertTrue(field in ciudad)

    def test_ciudades_por_id(self):
        """Debe devolver una ciudad en particular cuando se manda el ID por parametro"""
        ciudad = CiudadFactory(nombre='La Plata')
        response = self.app.get('/api/ciudades/{0}/'.format(ciudad.id))
        self.assertEqual(response.status, '200 OK')
        data = json.loads(response.content)
        self.assertTrue(type(data), dict)
        self.assertEqual(data['nombre'], 'La Plata')
        self.assertEqual(data['slug'], 'la-plata')
