# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-26 18:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compilacao', '0010_auto_20181004_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipotextoarticulado',
            name='rodape_global',
            field=models.TextField(default='', help_text='A cada Tipo de Texto Articulado pode ser adicionado uma nota global de rodapé!', verbose_name='Rodapé Global'),
        ),
    ]