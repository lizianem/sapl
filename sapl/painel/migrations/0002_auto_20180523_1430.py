# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-05-23 17:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('painel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cronometro',
            name='tipo',
            field=models.CharField(choices=[('A', 'Aparte'), ('D', 'Discurso'), ('O', 'Ordem do dia'), ('C', 'Considerações finais')], max_length=1, verbose_name='Tipo Cronômetro'),
        ),
    ]
