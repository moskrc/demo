# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-22 22:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0003_auto_20170521_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataplan',
            name='is_recommend',
            field=models.BooleanField(default=False, help_text='Highlight this data plan'),
        ),
    ]
