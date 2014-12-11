# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.core.management import call_command


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Poicb'
        db.create_table(u'catastro_poicb', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom_normal', self.gf('django.db.models.fields.TextField')()),
            ('nom', self.gf('django.db.models.fields.TextField')()),
            ('latlng', self.gf('django.contrib.gis.db.models.fields.GeometryField')(geography=True)),
        ))
        db.send_create_signal(u'catastro', ['Poicb'])


        # Changing field 'Poi.slug'
        db.alter_column(u'catastro_poi', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=150))

        # Add data migration
        call_command("loaddata", "apps/catastro/fixtures/poicb.json")

    def backwards(self, orm):
        # Deleting model 'Poicb'
        db.delete_table(u'catastro_poicb')


        # Changing field 'Poi.slug'
        #db.alter_column(u'catastro_poi', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=50))

    models = {
        u'catastro.calle': {
            'Meta': {'object_name': 'Calle'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.TextField', [], {}),
            'nom_normal': ('django.db.models.fields.TextField', [], {}),
            'way': ('django.contrib.gis.db.models.fields.GeometryField', [], {'geography': 'True'})
        },
        u'catastro.ciudad': {
            'Meta': {'object_name': 'Ciudad'},
            'activa': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'area_poligono': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'centro': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'envolvente': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_cuadrada': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'img_panorama': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'lineas': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['core.Linea']", 'null': 'True', 'blank': 'True'}),
            'longitud_poligono': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'poligono': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'provincia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catastro.Provincia']"}),
            'recorridos': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['core.Recorrido']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'blank': 'True'}),
            'sugerencia': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'variantes_nombre': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'zoom': ('django.db.models.fields.IntegerField', [], {'default': '14', 'null': 'True', 'blank': 'True'})
        },
        u'catastro.imagenciudad': {
            'Meta': {'object_name': 'ImagenCiudad'},
            'ciudad': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catastro.Ciudad']"}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'catastro.poi': {
            'Meta': {'object_name': 'Poi'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latlng': ('django.contrib.gis.db.models.fields.GeometryField', [], {'geography': 'True'}),
            'nom': ('django.db.models.fields.TextField', [], {}),
            'nom_normal': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '150'})
        },
        u'catastro.poicb': {
            'Meta': {'object_name': 'Poicb'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latlng': ('django.contrib.gis.db.models.fields.GeometryField', [], {'geography': 'True'}),
            'nom': ('django.db.models.fields.TextField', [], {}),
            'nom_normal': ('django.db.models.fields.TextField', [], {})
        },
        u'catastro.provincia': {
            'Meta': {'object_name': 'Provincia'},
            'area_poligono': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'centro': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'longitud_poligono': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'poligono': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'blank': 'True'}),
            'variantes_nombre': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'})
        },
        u'catastro.zona': {
            'Meta': {'object_name': 'Zona'},
            'geo': ('django.contrib.gis.db.models.fields.GeometryField', [], {'geography': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.linea': {
            'Meta': {'object_name': 'Linea'},
            'color_polilinea': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'cp': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'envolvente': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'foto': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_cuadrada': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'img_panorama': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'info_empresa': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'info_terminal': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'localidad': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'blank': 'True'}),
            'telefono': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'core.recorrido': {
            'Meta': {'ordering': "['linea__nombre', 'nombre']", 'object_name': 'Recorrido'},
            'color_polilinea': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fin': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'horarios': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_cuadrada': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'img_panorama': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'inicio': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'linea': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Linea']"}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'paradas_completas': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pois': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ruta': ('django.contrib.gis.db.models.fields.LineStringField', [], {}),
            'semirrapido': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sentido': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        }
    }

    complete_apps = ['catastro']