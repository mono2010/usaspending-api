# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-31 13:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('awards', '0052_transactiondelta'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transactionnormalized',
            name='generated_unique_award_id',
        ),
    ]