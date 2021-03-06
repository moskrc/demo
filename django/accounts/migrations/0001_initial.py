# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-22 20:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                # ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('type', models.IntegerField()),
                ('username', models.CharField(max_length=32)),
                ('password', models.CharField(max_length=32)),
                ('email', models.CharField(max_length=32)),
                ('token', models.CharField(max_length=32)),
                ('owner', models.IntegerField(blank=True, null=True)),
                ('suspended', models.IntegerField(blank=True, null=True)),
                ('validated', models.IntegerField()),
                ('added_date', models.IntegerField(blank=True, null=True)),
                ('timezone', models.CharField(max_length=32)),
                ('last_ip', models.CharField(max_length=32)),
                ('last_login', models.IntegerField(blank=True, null=True)),
                ('first_name', models.CharField(max_length=32)),
                ('last_name', models.CharField(max_length=32)),
                ('country', models.CharField(max_length=32)),
                ('mobile', models.IntegerField(blank=True, null=True)),
                # ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                # ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'users',
            },
        ),
    ]
