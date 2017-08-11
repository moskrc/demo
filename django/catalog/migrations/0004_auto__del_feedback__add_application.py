# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Feedback'
        db.delete_table(u'catalog_feedback')

        # Adding model 'Application'
        db.create_table(u'catalog_application', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.Item'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('about', self.gf('django.db.models.fields.TextField')(max_length=2048)),
        ))
        db.send_create_signal(u'catalog', ['Application'])


    def backwards(self, orm):
        # Adding model 'Feedback'
        db.create_table(u'catalog_feedback', (
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.Item'])),
            ('about', self.gf('django.db.models.fields.TextField')(max_length=2048)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'catalog', ['Feedback'])

        # Deleting model 'Application'
        db.delete_table(u'catalog_application')


    models = {
        u'catalog.application': {
            'Meta': {'object_name': 'Application'},
            'about': ('django.db.models.fields.TextField', [], {'max_length': '2048'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalog.Item']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'catalog.item': {
            'Meta': {'object_name': 'Item'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'employer_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'employer_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'employer_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'on_site': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'salary': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'secret_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['catalog']