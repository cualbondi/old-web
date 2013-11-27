# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Anuncio'
        db.create_table('anuncios_anuncio', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('img', self.gf('django.db.models.fields.files.ImageField')(max_length=500)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=500)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('activo', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('orden', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('anuncios', ['Anuncio'])

        # Adding M2M table for field ciudades on 'Anuncio'
        m2m_table_name = db.shorten_name('anuncios_anuncio_ciudades')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('anuncio', models.ForeignKey(orm['anuncios.anuncio'], null=False)),
            ('ciudad', models.ForeignKey(orm['catastro.ciudad'], null=False))
        ))
        db.create_unique(m2m_table_name, ['anuncio_id', 'ciudad_id'])


    def backwards(self, orm):
        # Deleting model 'Anuncio'
        db.delete_table('anuncios_anuncio')

        # Removing M2M table for field ciudades on 'Anuncio'
        db.delete_table(db.shorten_name('anuncios_anuncio_ciudades'))


    models = {
        'anuncios.anuncio': {
            'Meta': {'object_name': 'Anuncio'},
            'activo': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ciudades': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'anuncios'", 'symmetrical': 'False', 'to': "orm['catastro.Ciudad']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': '500'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '500'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'orden': ('django.db.models.fields.IntegerField', [], {})
        },
        'catastro.ciudad': {
            'Meta': {'object_name': 'Ciudad'},
            'activa': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'area_poligono': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2', 'blank': 'True'}),
            'centro': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'envolvente': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_cuadrada': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'img_panorama': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
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
        'core.linea': {
            'Meta': {'object_name': 'Linea'},
            'color_polilinea': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'cp': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'envolvente': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'foto': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_cuadrada': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'img_panorama': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
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
            'img_cuadrada': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'img_panorama': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
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

    complete_apps = ['anuncios']