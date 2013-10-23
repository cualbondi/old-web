# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Linea'
        db.create_table('core_linea', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=120, blank=True)),
            ('descripcion', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('foto', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('color_polilinea', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('info_empresa', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('info_terminal', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('localidad', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('cp', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('telefono', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('envolvente', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Linea'])

        # Adding model 'Recorrido'
        db.create_table('core_recorrido', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('linea', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Linea'])),
            ('ruta', self.gf('django.contrib.gis.db.models.fields.LineStringField')()),
            ('sentido', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200, blank=True)),
            ('inicio', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('fin', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('semirrapido', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('color_polilinea', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('horarios', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('pois', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('descripcion', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('paradas_completas', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('core', ['Recorrido'])

        # Adding model 'Comercio'
        db.create_table('core_comercio', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('latlng', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('ciudad', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catastro.Ciudad'])),
        ))
        db.send_create_signal('core', ['Comercio'])

        # Adding model 'Parada'
        db.create_table('core_parada', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('codigo', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('latlng', self.gf('django.contrib.gis.db.models.fields.PointField')()),
        ))
        db.send_create_signal('core', ['Parada'])

        # Adding model 'Horario'
        db.create_table('core_horario', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recorrido', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Recorrido'])),
            ('parada', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Parada'])),
            ('hora', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Horario'])

        # Adding model 'Terminal'
        db.create_table('core_terminal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('linea', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Linea'])),
            ('descripcion', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('direccion', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('telefono', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('latlng', self.gf('django.contrib.gis.db.models.fields.PointField')()),
        ))
        db.send_create_signal('core', ['Terminal'])

        # Adding model 'Tarifa'
        db.create_table('core_tarifa', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('precio', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('ciudad', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catastro.Ciudad'])),
        ))
        db.send_create_signal('core', ['Tarifa'])


    def backwards(self, orm):
        # Deleting model 'Linea'
        db.delete_table('core_linea')

        # Deleting model 'Recorrido'
        db.delete_table('core_recorrido')

        # Deleting model 'Comercio'
        db.delete_table('core_comercio')

        # Deleting model 'Parada'
        db.delete_table('core_parada')

        # Deleting model 'Horario'
        db.delete_table('core_horario')

        # Deleting model 'Terminal'
        db.delete_table('core_terminal')

        # Deleting model 'Tarifa'
        db.delete_table('core_tarifa')


    models = {
        'catastro.ciudad': {
            'Meta': {'object_name': 'Ciudad'},
            'activa': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'area_poligono': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'centro': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'envolvente': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lineas': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['core.Linea']", 'null': 'True', 'blank': 'True'}),
            'longitud_poligono': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'poligono': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'provincia': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catastro.Provincia']"}),
            'recorridos': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['core.Recorrido']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'blank': 'True'}),
            'sugerencia': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'variantes_nombre': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'zoom': ('django.db.models.fields.IntegerField', [], {'default': '14', 'null': 'True', 'blank': 'True'})
        },
        'catastro.provincia': {
            'Meta': {'object_name': 'Provincia'},
            'area_poligono': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'centro': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'longitud_poligono': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'poligono': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'blank': 'True'}),
            'variantes_nombre': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'})
        },
        'core.comercio': {
            'Meta': {'object_name': 'Comercio'},
            'ciudad': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catastro.Ciudad']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latlng': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.horario': {
            'Meta': {'object_name': 'Horario'},
            'hora': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parada': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Parada']"}),
            'recorrido': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Recorrido']"})
        },
        'core.linea': {
            'Meta': {'object_name': 'Linea'},
            'color_polilinea': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'cp': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'envolvente': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'foto': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_empresa': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'info_terminal': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'localidad': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'blank': 'True'}),
            'telefono': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'core.parada': {
            'Meta': {'object_name': 'Parada'},
            'codigo': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latlng': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'core.recorrido': {
            'Meta': {'ordering': "['linea__nombre', 'nombre']", 'object_name': 'Recorrido'},
            'color_polilinea': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fin': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'horarios': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'linea': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Linea']"}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'paradas_completas': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pois': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ruta': ('django.contrib.gis.db.models.fields.LineStringField', [], {}),
            'semirrapido': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sentido': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'blank': 'True'})
        },
        'core.tarifa': {
            'Meta': {'object_name': 'Tarifa'},
            'ciudad': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catastro.Ciudad']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'precio': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'core.terminal': {
            'Meta': {'object_name': 'Terminal'},
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'direccion': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latlng': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'linea': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Linea']"}),
            'telefono': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        }
    }

    complete_apps = ['core']