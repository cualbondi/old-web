# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Calle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('way', django.contrib.gis.db.models.fields.GeometryField(srid=4326, geography=True)),
                ('nom_normal', models.TextField()),
                ('nom', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Ciudad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=120, blank=True)),
                ('activa', models.BooleanField(default=False)),
                ('img_panorama', models.ImageField(max_length=200, null=True, upload_to=b'ciudad', blank=True)),
                ('img_cuadrada', models.ImageField(max_length=200, null=True, upload_to=b'ciudad', blank=True)),
                ('variantes_nombre', models.CharField(max_length=150, null=True, blank=True)),
                ('longitud_poligono', models.DecimalField(null=True, max_digits=7, decimal_places=2, blank=True)),
                ('area_poligono', models.DecimalField(null=True, max_digits=7, decimal_places=2, blank=True)),
                ('poligono', django.contrib.gis.db.models.fields.PolygonField(srid=4326, null=True, blank=True)),
                ('envolvente', django.contrib.gis.db.models.fields.PolygonField(srid=4326, null=True, blank=True)),
                ('zoom', models.IntegerField(default=14, null=True, blank=True)),
                ('centro', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('sugerencia', models.CharField(max_length=100, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ImagenCiudad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('original', models.ImageField(upload_to=b'img/ciudades')),
                ('titulo', models.CharField(max_length=100, null=True, blank=True)),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('ciudad', models.ForeignKey(to='catastro.Ciudad')),
            ],
        ),
        migrations.CreateModel(
            name='Poi',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom_normal', models.TextField()),
                ('nom', models.TextField()),
                ('slug', models.SlugField(max_length=150)),
                ('latlng', django.contrib.gis.db.models.fields.GeometryField(srid=4326, geography=True)),
            ],
        ),
        migrations.CreateModel(
            name='Poicb',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom_normal', models.TextField(blank=True)),
                ('nom', models.TextField()),
                ('latlng', django.contrib.gis.db.models.fields.GeometryField(srid=4326, geography=True)),
            ],
        ),
        migrations.CreateModel(
            name='Provincia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=120, blank=True)),
                ('variantes_nombre', models.CharField(max_length=150, null=True, blank=True)),
                ('longitud_poligono', models.DecimalField(null=True, max_digits=7, decimal_places=2, blank=True)),
                ('area_poligono', models.DecimalField(null=True, max_digits=7, decimal_places=2, blank=True)),
                ('centro', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('poligono', django.contrib.gis.db.models.fields.PolygonField(srid=4326, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Zona',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('geo', django.contrib.gis.db.models.fields.GeometryField(srid=4326, geography=True)),
            ],
        ),
    ]
