# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import apps.editor.fields
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogModeracion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_create', models.DateTimeField(auto_now_add=True)),
                ('newStatus', models.CharField(default=b'E', max_length=1, choices=[(b'E', b'Esperando Mod'), (b'S', b'Aceptado'), (b'N', b'Rechazado'), (b'R', b'Retirado')])),
                ('created_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RecorridoProposed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parent', models.CharField(max_length=36)),
                ('uuid', models.CharField(max_length=36)),
                ('nombre', models.CharField(max_length=100)),
                ('ruta', django.contrib.gis.db.models.fields.LineStringField(srid=4326)),
                ('sentido', models.CharField(max_length=100, null=True, blank=True)),
                ('slug', models.SlugField(max_length=200, null=True, blank=True)),
                ('inicio', models.CharField(max_length=100, null=True, blank=True)),
                ('fin', models.CharField(max_length=100, null=True, blank=True)),
                ('semirrapido', models.BooleanField(default=False)),
                ('color_polilinea', models.CharField(max_length=20, null=True, blank=True)),
                ('horarios', models.TextField(null=True, blank=True)),
                ('pois', models.TextField(null=True, blank=True)),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('current_status', models.CharField(default=b'E', max_length=1, choices=[(b'E', b'Esperando Mod'), (b'S', b'Aceptado'), (b'N', b'Rechazado'), (b'R', b'Retirado')])),
                ('date_create', models.DateTimeField(auto_now_add=True)),
                ('date_update', models.DateTimeField(auto_now=True)),
                ('paradas_completas', models.BooleanField(default=False)),
                ('linea', models.ForeignKey(to='core.Linea')),
                ('recorrido', models.ForeignKey(to='core.Recorrido')),
            ],
            options={
                'permissions': (('moderate_recorridos', 'Can moderate (accept/decline) recorridos'),),
            },
        ),
        migrations.AddField(
            model_name='logmoderacion',
            name='recorridoProposed',
            field=models.ForeignKey(to='editor.RecorridoProposed'),
        ),
    ]
