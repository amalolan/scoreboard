# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-23 14:26
from __future__ import unicode_literals

from django.db import migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0019_auto_20171223_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='board',
            field=picklefield.fields.PickledObjectField(default=[], editable=False),
        ),
    ]
