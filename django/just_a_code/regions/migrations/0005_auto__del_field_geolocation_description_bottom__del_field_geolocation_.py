# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'GeoLocation.description_bottom'
        db.delete_column('regions_geolocation', 'description_bottom')

        # Deleting field 'GeoLocation.description_top'
        db.delete_column('regions_geolocation', 'description_top')

        # Adding field 'GeoLocation.description'
        db.add_column('regions_geolocation', 'description',
                      self.gf('django.db.models.fields.TextField')(max_length=2048, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'GeoLocation.description_bottom'
        db.add_column('regions_geolocation', 'description_bottom',
                      self.gf('django.db.models.fields.TextField')(max_length=2048, null=True, blank=True),
                      keep_default=False)

        # Adding field 'GeoLocation.description_top'
        db.add_column('regions_geolocation', 'description_top',
                      self.gf('django.db.models.fields.TextField')(max_length=2048, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'GeoLocation.description'
        db.delete_column('regions_geolocation', 'description')


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
            'Meta': {'ordering': "['weight', 'name']", 'object_name': 'GeoLocation'},
            'biggest_city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lat': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'lng': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'metro': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'region': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'my_custom_location'", 'unique': 'True', 'to': "orm['django_geoip.Region']"}),
            'subdomain': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'zoom': ('django.db.models.fields.IntegerField', [], {'default': '13'})
        }
    }

    complete_apps = ['regions']