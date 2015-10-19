from rest_framework.test import APITestCase
from rest_framework import status
from apps.catastro.models import Provincia, Ciudad


class TestCiudades(APITestCase):

    def test_cant(self):
        """ Should add and return one Ciudad """
        p = Provincia.objects.create(nombre='Bs As')
        Ciudad.objects.create(nombre='La Plata', provincia=p, activa=True)

        response = self.client.get('/api/v2/ciudades/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
