# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2020-06-22 15:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_auto_20200622_2339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='enrolled_date',
            field=models.DateTimeField(auto_now=True, verbose_name='报名日期'),
        ),
    ]
