# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-17 04:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20171017_0359'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagesheet',
            name='state',
            field=models.CharField(choices=[('FR', 'Fresh'), ('PI', 'Processing'), ('DS', 'Processed'), ('DE', 'ProcessedWithError')], default='FR', max_length=20),
        ),
    ]
