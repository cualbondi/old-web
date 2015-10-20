# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catastro', '0002_auto_20151019_1835'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomPoi',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
                ('latlng', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('usuario', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PerfilUsuario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=50, null=True, blank=True)),
                ('apellido', models.CharField(max_length=50, null=True, blank=True)),
                ('about', models.TextField(null=True, blank=True)),
                ('website', models.URLField(null=True, blank=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('ultima_modificacion', models.DateTimeField(auto_now=True)),
                ('confirmacion_key', models.CharField(max_length=40)),
                ('fecha_envio_confirmacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_verificacion', models.DateTimeField(default=None, null=True, blank=True)),
                ('ciudad', models.ForeignKey(blank=True, to='catastro.Ciudad', null=True)),
                ('usuario', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RecorridoFavorito',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activo', models.BooleanField()),
                ('recorrido', models.ForeignKey(to='core.Recorrido')),
                ('usuario', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
