# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Provincia'
        db.create_table('catastro_provincia', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=120, blank=True)),
            ('variantes_nombre', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('longitud_poligono', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=2, blank=True)),
            ('area_poligono', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=2, blank=True)),
            ('centro', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True, blank=True)),
            ('poligono', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True)),
        ))
        db.send_create_signal('catastro', ['Provincia'])

        # Adding model 'Ciudad'
        db.create_table('catastro_ciudad', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=120, blank=True)),
            ('provincia', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catastro.Provincia'])),
            ('activa', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('variantes_nombre', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('longitud_poligono', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=2, blank=True)),
            ('area_poligono', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=2, blank=True)),
            ('poligono', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True)),
            ('envolvente', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True)),
            ('zoom', self.gf('django.db.models.fields.IntegerField')(default=14, null=True, blank=True)),
            ('centro', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True, blank=True)),
            ('descripcion', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('sugerencia', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('catastro', ['Ciudad'])

        # Adding M2M table for field recorridos on 'Ciudad'
        db.create_table('catastro_ciudad_recorridos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ciudad', models.ForeignKey(orm['catastro.ciudad'], null=False)),
            ('recorrido', models.ForeignKey(orm['core.recorrido'], null=False))
        ))
        db.create_unique('catastro_ciudad_recorridos', ['ciudad_id', 'recorrido_id'])

        # Adding M2M table for field lineas on 'Ciudad'
        db.create_table('catastro_ciudad_lineas', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ciudad', models.ForeignKey(orm['catastro.ciudad'], null=False)),
            ('linea', models.ForeignKey(orm['core.linea'], null=False))
        ))
        db.create_unique('catastro_ciudad_lineas', ['ciudad_id', 'linea_id'])

        # Adding model 'ImagenCiudad'
        db.create_table('catastro_imagenciudad', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ciudad', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catastro.Ciudad'])),
            ('original', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('titulo', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('descripcion', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('catastro', ['ImagenCiudad'])

        # Adding model 'Zona'
        db.create_table('catastro_zona', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('geo', self.gf('django.contrib.gis.db.models.fields.GeometryField')(geography=True)),
        ))
        db.send_create_signal('catastro', ['Zona'])

        # Adding model 'Calle'
        db.create_table('catastro_calle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('way', self.gf('django.contrib.gis.db.models.fields.GeometryField')(geography=True)),
            ('nom_normal', self.gf('django.db.models.fields.TextField')()),
            ('nom', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('catastro', ['Calle'])

        # Adding model 'Poi'
        db.create_table('catastro_poi', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom_normal', self.gf('django.db.models.fields.TextField')()),
            ('nom', self.gf('django.db.models.fields.TextField')()),
            ('latlng', self.gf('django.contrib.gis.db.models.fields.PointField')()),
        ))
        db.send_create_signal('catastro', ['Poi'])


    def backwards(self, orm):
        # Deleting model 'Provincia'
        db.delete_table('catastro_provincia')

        # Deleting model 'Ciudad'
        db.delete_table('catastro_ciudad')

        # Removing M2M table for field recorridos on 'Ciudad'
        db.delete_table('catastro_ciudad_recorridos')

        # Removing M2M table for field lineas on 'Ciudad'
        db.delete_table('catastro_ciudad_lineas')

        # Deleting model 'ImagenCiudad'
        db.delete_table('catastro_imagenciudad')

        # Deleting model 'Zona'
        db.delete_table('catastro_zona')

        # Deleting model 'Calle'
        db.delete_table('catastro_calle')

        # Deleting model 'Poi'
        db.delete_table('catastro_poi')


    models = {
        'catastro.calle': {
            'Meta': {'object_name': 'Calle'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.TextField', [], {}),
            'nom_normal': ('django.db.models.fields.TextField', [], {}),
            'way': ('django.contrib.gis.db.models.fields.GeometryField', [], {'geography': 'True'})
        },
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
        'catastro.imagenciudad': {
            'Meta': {'object_name': 'ImagenCiudad'},
            'ciudad': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catastro.Ciudad']"}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'catastro.poi': {
            'Meta': {'object_name': 'Poi'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latlng': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'nom': ('django.db.models.fields.TextField', [], {}),
            'nom_normal': ('django.db.models.fields.TextField', [], {})
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
        'catastro.zona': {
            'Meta': {'object_name': 'Zona'},
            'geo': ('django.contrib.gis.db.models.fields.GeometryField', [], {'geography': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        }
    }

    complete_apps = ['catastro']