# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-23 08:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_auto_20171122_2107'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserNeuralNet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(help_text='Username', max_length=50)),
                ('data_name', models.CharField(help_text='Data name', max_length=20)),
                ('file_path', models.CharField(help_text='S3 relative file path', max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='userneuralnet',
            unique_together=set([('username', 'data_name')]),
        ),
    ]
