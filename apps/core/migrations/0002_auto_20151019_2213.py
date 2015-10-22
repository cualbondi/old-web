# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            [('ALTER TABLE core_recorrido ALTER COLUMN uuid TYPE uuid USING greatest(uuid,\'00000000000000000000000000000000\')::uuid;')],
            [('ALTER TABLE core_recorrido ALTER COLUMN uuid TYPE varchar(36) USING uuid::varchar(36);')],
        )
    ]
