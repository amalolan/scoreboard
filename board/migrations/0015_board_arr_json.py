# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-23 11:18
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0014_auto_20171223_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='arr_json',
            field=jsonfield.fields.JSONField(null=True, verbose_name=[1, 2, 3]),
        ),
    ]