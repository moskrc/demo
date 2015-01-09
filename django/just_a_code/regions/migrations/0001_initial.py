# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GeoLocation'
        db.create_table('regions_geolocation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('region', self.gf('django.db.models.fields.related.OneToOneField')(related_name='my_custom_location', unique=True, to=orm['django_geoip.Region'])),
            ('is_default', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lat', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('lng', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('zoom', self.gf('django.db.models.fields.IntegerField')(default=13)),
            ('biggest_city', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('metro', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('regions', ['GeoLocation'])


    def backwards(self, orm):
        # Deleting model 'GeoLocation'
        db.delete_table('regions_geolocation')


    models = {
        'django_geoip.country': {
            'Meta': {'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'django_geoip.region': {
            'Meta': {'unique_together': "(('country', 'name'),)", 'object_name': 'Region'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'regions'", 'to': "orm['django_geoip.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'regions.geolocation': {
            'Meta': {'object_name': 'GeoLocation'},
            'biggest_city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lat': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'lng': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'metro': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'region': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'my_custom_location'", 'unique': 'True', 'to': "orm['django_geoip.Region']"}),
            'zoom': ('django.db.models.fields.IntegerField', [], {'default': '13'})
        }
    }

    complete_apps = ['regions']