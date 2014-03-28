# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Version'
        db.create_table('mobile_updates_version', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('noticia', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('mobile_updates', ['Version'])


    def backwards(self, orm):
        # Deleting model 'Version'
        db.delete_table('mobile_updates_version')


    models = {
        'mobile_updates.version': {
            'Meta': {'object_name': 'Version'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'noticia': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        }
    }

    complete_apps = ['mobile_updates']