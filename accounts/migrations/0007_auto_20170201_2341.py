# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-01 20:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20170201_2223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='timestamp',
            field=models.DateTimeField(),
        ),
    ]
