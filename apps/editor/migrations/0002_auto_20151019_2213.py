# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            [('ALTER TABLE editor_recorridoproposed ALTER COLUMN uuid TYPE uuid USING GREATEST(uuid,\'00000000000000000000000000000000\')::uuid;')],
            [('ALTER TABLE editor_recorridoproposed ALTER COLUMN uuid TYPE varchar(36) USING uuid::varchar(36);')],
        ),
        migrations.RunSQL(
            [('ALTER TABLE editor_recorridoproposed ALTER COLUMN parent TYPE uuid USING GREATEST(parent,\'00000000000000000000000000000000\')::uuid;')],
            [('ALTER TABLE editor_recorridoproposed ALTER COLUMN parent TYPE varchar(36) USING parent::varchar(36);')],
        ),
        migrations.AlterField(
            model_name='recorridoproposed',
            name='parent',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='recorridoproposed',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
