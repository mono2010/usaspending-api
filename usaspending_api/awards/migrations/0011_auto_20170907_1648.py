# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-07 16:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('awards', '0010_indices_d1_d2_c'),
    ]

    operations = [
        migrations.AlterField(
            model_name='award',
            name='category',
            field=models.TextField(help_text="A field that generalizes the award's type.", null=True, verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='award',
            name='type',
            field=models.TextField(db_index=True, help_text='The mechanism used to distribute funding. The federal government can distribute funding in several forms. These award types include contracts, grants, loans, and direct payments.', null=True, verbose_name='Award Type'),
        ),
    ]