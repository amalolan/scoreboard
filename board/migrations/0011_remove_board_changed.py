# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-22 11:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0010_auto_20171222_1616'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='board',
            name='changed',
        ),
    ]
