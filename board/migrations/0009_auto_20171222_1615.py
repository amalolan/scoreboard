# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-22 10:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0008_auto_20171222_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tempbool',
            name='team',
            field=models.IntegerField(),
        ),
    ]
