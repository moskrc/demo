# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ChatRoom'
        db.create_table('chat_chatroom', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, blank=True)),
        ))
        db.send_create_signal('chat', ['ChatRoom'])

        # Adding model 'ChatUser'
        db.create_table('chat_chatuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('session', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(related_name='users', to=orm['chat.ChatRoom'])),
        ))
        db.send_create_signal('chat', ['ChatUser'])


    def backwards(self, orm):
        # Deleting model 'ChatRoom'
        db.delete_table('chat_chatroom')

        # Deleting model 'ChatUser'
        db.delete_table('chat_chatuser')


    models = {
        'chat.chatroom': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ChatRoom'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'})
        },
        'chat.chatuser': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ChatUser'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'users'", 'to': "orm['chat.ChatRoom']"}),
            'session': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['chat']