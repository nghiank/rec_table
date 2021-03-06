# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-22 21:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_auto_20171107_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='cell',
            name='file_path',
            field=models.CharField(default=' ', help_text='S3 relative file path', max_length=254),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='cell',
            unique_together=set([('image_sheet', 'file_path')]),
        ),
    ]
