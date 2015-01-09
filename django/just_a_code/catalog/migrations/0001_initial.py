# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DealType'
        db.create_table('catalog_dealtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('show_commission_field', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_pledge_field', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_period_field', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_price_field', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('catalog', ['DealType'])

        # Adding model 'FieldSet'
        db.create_table('catalog_fieldset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('catalog', ['FieldSet'])

        # Adding model 'Field'
        db.create_table('catalog_field', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.CharField')(default='CharField', max_length=255)),
            ('additional_info', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('field_set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.FieldSet'])),
            ('css_class', self.gf('django.db.models.fields.CharField')(default='input-xxlarge', max_length=255, null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('catalog', ['Field'])

        # Adding model 'CatetegoryTypeFieldValue'
        db.create_table('catalog_catetegorytypefieldvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['catalog.Category'])),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.Field'])),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('value_bool', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('value_text', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('catalog', ['CatetegoryTypeFieldValue'])

        # Adding M2M table for field value_choice on 'CatetegoryTypeFieldValue'
        db.create_table('catalog_catetegorytypefieldvalue_value_choice', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('catetegorytypefieldvalue', models.ForeignKey(orm['catalog.catetegorytypefieldvalue'], null=False)),
            ('dict', models.ForeignKey(orm['dict.dict'], null=False))
        ))
        db.create_unique('catalog_catetegorytypefieldvalue_value_choice', ['catetegorytypefieldvalue_id', 'dict_id'])

        # Adding M2M table for field deal_types on 'CatetegoryTypeFieldValue'
        db.create_table('catalog_catetegorytypefieldvalue_deal_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('catetegorytypefieldvalue', models.ForeignKey(orm['catalog.catetegorytypefieldvalue'], null=False)),
            ('dealtype', models.ForeignKey(orm['catalog.dealtype'], null=False))
        ))
        db.create_unique('catalog_catetegorytypefieldvalue_deal_types', ['catetegorytypefieldvalue_id', 'dealtype_id'])

        # Adding model 'Category'
        db.create_table('catalog_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='childrens', null=True, to=orm['catalog.Category'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('show_additional_price_options', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('small_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('show_on_main', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('catalog', ['Category'])

        # Adding M2M table for field deal_types on 'Category'
        db.create_table('catalog_category_deal_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('category', models.ForeignKey(orm['catalog.category'], null=False)),
            ('dealtype', models.ForeignKey(orm['catalog.dealtype'], null=False))
        ))
        db.create_unique('catalog_category_deal_types', ['category_id', 'dealtype_id'])

        # Adding model 'Product'
        db.create_table('catalog_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('deal_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.DealType'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='products', to=orm['catalog.Category'])),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=1024, blank=True)),
            ('data', self.gf('django_hstore.hstore.DictionaryField')(db_index=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('is_approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('paid_until', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 2, 20, 0, 0), blank=True)),
        ))
        db.send_create_signal('catalog', ['Product'])

        # Adding model 'Price'
        db.create_table('catalog_price', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='prices', to=orm['catalog.Product'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=0, blank=True)),
            ('price_type', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('price_period', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('commission', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=0, blank=True)),
            ('pledge', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=0, blank=True)),
        ))
        db.send_create_signal('catalog', ['Price'])

        # Adding model 'Location'
        db.create_table('catalog_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='locations', to=orm['catalog.Product'])),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['regions.GeoLocation'])),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('lat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('lng', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('zoom_level', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('metro_available', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('metro', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('metro_dist', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('metro_dist_type', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('metro_alt', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('metro_alt_dist', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('metro_alt_dist_type', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('catalog', ['Location'])

        # Adding model 'ProductImage'
        db.create_table('catalog_productimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='images', to=orm['catalog.Product'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal('catalog', ['ProductImage'])


    def backwards(self, orm):
        # Deleting model 'DealType'
        db.delete_table('catalog_dealtype')

        # Deleting model 'FieldSet'
        db.delete_table('catalog_fieldset')

        # Deleting model 'Field'
        db.delete_table('catalog_field')

        # Deleting model 'CatetegoryTypeFieldValue'
        db.delete_table('catalog_catetegorytypefieldvalue')

        # Removing M2M table for field value_choice on 'CatetegoryTypeFieldValue'
        db.delete_table('catalog_catetegorytypefieldvalue_value_choice')

        # Removing M2M table for field deal_types on 'CatetegoryTypeFieldValue'
        db.delete_table('catalog_catetegorytypefieldvalue_deal_types')

        # Deleting model 'Category'
        db.delete_table('catalog_category')

        # Removing M2M table for field deal_types on 'Category'
        db.delete_table('catalog_category_deal_types')

        # Deleting model 'Product'
        db.delete_table('catalog_product')

        # Deleting model 'Price'
        db.delete_table('catalog_price')

        # Deleting model 'Location'
        db.delete_table('catalog_location')

        # Deleting model 'ProductImage'
        db.delete_table('catalog_productimage')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'catalog.category': {
            'Meta': {'object_name': 'Category'},
            'deal_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['catalog.DealType']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'childrens'", 'null': 'True', 'to': "orm['catalog.Category']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'show_additional_price_options': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_on_main': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'small_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'catalog.catetegorytypefieldvalue': {
            'Meta': {'object_name': 'CatetegoryTypeFieldValue'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['catalog.Category']"}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'deal_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['catalog.DealType']", 'symmetrical': 'False'}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'value_bool': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'value_choice': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'choices'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dict.Dict']"}),
            'value_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'catalog.dealtype': {
            'Meta': {'object_name': 'DealType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'show_commission_field': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_period_field': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_pledge_field': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_price_field': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        'catalog.field': {
            'Meta': {'ordering': "['field_set']", 'object_name': 'Field'},
            'additional_info': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'css_class': ('django.db.models.fields.CharField', [], {'default': "'input-xxlarge'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'field_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.FieldSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'CharField'", 'max_length': '255'})
        },
        'catalog.fieldset': {
            'Meta': {'ordering': "['weight']", 'object_name': 'FieldSet'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'catalog.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lng': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'metro': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'metro_alt': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'metro_alt_dist': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'metro_alt_dist_type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'metro_available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'metro_dist': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'metro_dist_type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'locations'", 'to': "orm['catalog.Product']"}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['regions.GeoLocation']"}),
            'zoom_level': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'catalog.price': {
            'Meta': {'object_name': 'Price'},
            'commission': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '0', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'pledge': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '0', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '0', 'blank': 'True'}),
            'price_period': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'price_type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'prices'", 'to': "orm['catalog.Product']"})
        },
        'catalog.product': {
            'Meta': {'object_name': 'Product'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'to': "orm['catalog.Category']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'data': ('django_hstore.hstore.DictionaryField', [], {'db_index': 'True'}),
            'deal_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalog.DealType']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'paid_until': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 2, 20, 0, 0)', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'catalog.productimage': {
            'Meta': {'object_name': 'ProductImage'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': "orm['catalog.Product']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dict.dict': {
            'Meta': {'object_name': 'Dict'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['dict.Dict']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
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
            'seo_description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'seo_keywords': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'seo_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'subdomain': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'zoom': ('django.db.models.fields.IntegerField', [], {'default': '13'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['catalog']