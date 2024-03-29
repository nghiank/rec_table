# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-17 03:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ImageSheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='unknown', help_text='Username', max_length=50)),
                ('file_id', models.CharField(help_text='File Id', max_length=120)),
                ('url', models.CharField(help_text='File URL', max_length=250)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
