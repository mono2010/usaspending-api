# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-09-18 00:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('awards', '0064_solicitation_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='award',
            name='potential_total_value_of_award',
        ),
        migrations.RemoveField(
            model_name='award',
            name='total_outlay',
        ),
    ]