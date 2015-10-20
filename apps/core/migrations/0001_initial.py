# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import apps.editor.fields
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catastro', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comercio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
                ('latlng', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('ciudad', models.ForeignKey(to='catastro.Ciudad')),
            ],
        ),
        migrations.CreateModel(
            name='FacebookPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('id_fb', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Horario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hora', models.CharField(max_length=5, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Linea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=120, blank=True)),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('foto', models.CharField(max_length=20, null=True, blank=True)),
                ('img_panorama', models.ImageField(max_length=200, null=True, upload_to=b'linea', blank=True)),
                ('img_cuadrada', models.ImageField(max_length=200, null=True, upload_to=b'linea', blank=True)),
                ('color_polilinea', models.CharField(max_length=20, null=True, blank=True)),
                ('info_empresa', models.TextField(null=True, blank=True)),
                ('info_terminal', models.TextField(null=True, blank=True)),
                ('localidad', models.CharField(max_length=50, null=True, blank=True)),
                ('cp', models.CharField(max_length=20, null=True, blank=True)),
                ('telefono', models.CharField(max_length=200, null=True, blank=True)),
                ('envolvente', django.contrib.gis.db.models.fields.PolygonField(srid=4326, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Parada',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo', models.CharField(max_length=15, null=True, blank=True)),
                ('nombre', models.CharField(max_length=100, null=True, blank=True)),
                ('latlng', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='Posicion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dispositivo_uuid', models.CharField(max_length=100, null=True, blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('latlng', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={
                'verbose_name': 'Posicion',
                'verbose_name_plural': 'Posiciones',
            },
        ),
        migrations.CreateModel(
            name='Recorrido',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', apps.editor.fields.UUIDField(max_length=36, editable=False, blank=True)),
                ('nombre', models.CharField(max_length=100)),
                ('img_panorama', models.ImageField(max_length=200, null=True, upload_to=b'recorrido', blank=True)),
                ('img_cuadrada', models.ImageField(max_length=200, null=True, upload_to=b'recorrido', blank=True)),
                ('ruta', django.contrib.gis.db.models.fields.LineStringField(srid=4326)),
                ('sentido', models.CharField(max_length=100, blank=True)),
                ('slug', models.SlugField(max_length=200, blank=True)),
                ('inicio', models.CharField(max_length=100, blank=True)),
                ('fin', models.CharField(max_length=100, blank=True)),
                ('semirrapido', models.BooleanField(default=False)),
                ('color_polilinea', models.CharField(max_length=20, null=True, blank=True)),
                ('horarios', models.TextField(null=True, blank=True)),
                ('pois', models.TextField(null=True, blank=True)),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('paradas_completas', models.BooleanField(default=False)),
                ('linea', models.ForeignKey(to='core.Linea')),
            ],
            options={
                'ordering': ['linea__nombre', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='Tarifa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.CharField(max_length=150)),
                ('precio', models.DecimalField(max_digits=5, decimal_places=2)),
                ('ciudad', models.ForeignKey(to='catastro.Ciudad')),
            ],
        ),
        migrations.CreateModel(
            name='Terminal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('direccion', models.CharField(max_length=150)),
                ('telefono', models.CharField(max_length=150)),
                ('latlng', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('linea', models.ForeignKey(to='core.Linea')),
            ],
        ),
        migrations.AddField(
            model_name='posicion',
            name='recorrido',
            field=models.ForeignKey(to='core.Recorrido'),
        ),
        migrations.AddField(
            model_name='horario',
            name='parada',
            field=models.ForeignKey(to='core.Parada'),
        ),
        migrations.AddField(
            model_name='horario',
            name='recorrido',
            field=models.ForeignKey(to='core.Recorrido'),
        ),
        migrations.AddField(
            model_name='facebookpage',
            name='linea',
            field=models.ForeignKey(to='core.Linea'),
        ),
    ]
