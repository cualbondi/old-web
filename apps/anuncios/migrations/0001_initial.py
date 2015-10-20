# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catastro', '0002_auto_20151019_1835'),
    ]

    operations = [
        migrations.CreateModel(
            name='Anuncio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
                ('img', models.ImageField(max_length=500, upload_to=b'anuncios')),
                ('link', models.URLField(max_length=500)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=False)),
                ('orden', models.IntegerField()),
                ('ciudades', models.ManyToManyField(related_name='anuncios', to='catastro.Ciudad')),
            ],
            options={
                'ordering': ['orden'],
            },
        ),
    ]
