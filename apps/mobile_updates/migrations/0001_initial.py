# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('name', models.CharField(max_length=20)),
                ('tipo', models.CharField(max_length=1, choices=[(b'a', b'Aplicacion android'), (b'l', b'Lineas'), (b'c', b'Ciudades')])),
                ('noticia', models.CharField(max_length=500)),
            ],
        ),
    ]
