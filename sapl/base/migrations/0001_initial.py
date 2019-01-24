# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-25 11:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('documentos_administrativos', models.CharField(choices=[('O', 'Ostensivo'), ('R', 'Restritivo')], default='O', max_length=1, verbose_name='Ostensivo/Restritivo')),
                ('sequencia_numeracao', models.CharField(choices=[('A', 'Sequencial por ano'), ('U', 'Sequencial único')], default='A', max_length=1, verbose_name='Sequência de numeração')),
                ('painel_aberto', models.BooleanField(choices=[(True, 'Sim'), (False, 'Não')], default=False, verbose_name='Painel aberto para usuário anônimo')),
                ('texto_articulado_proposicao', models.BooleanField(choices=[(True, 'Sim'), (False, 'Não')], default=False, verbose_name='Usar Textos Articulados para Proposições')),
                ('texto_articulado_materia', models.BooleanField(choices=[(True, 'Sim'), (False, 'Não')], default=False, verbose_name='Usar Textos Articulados para Matérias')),
                ('texto_articulado_norma', models.BooleanField(choices=[(True, 'Sim'), (False, 'Não')], default=True, verbose_name='Usar Textos Articulados para Normas')),
                ('proposicao_incorporacao_obrigatoria', models.CharField(choices=[('O', 'Sempre Gerar Protocolo'), ('C', 'Perguntar se é pra gerar protocolo ao incorporar'), ('N', 'Nunca Protocolar ao incorporar uma proposição')], default='O', max_length=1, verbose_name='Regra de incorporação de proposições e protocolo')),
                ('cronometro_discurso', models.TimeField(blank=True, null=True, verbose_name='Cronômetro do Discurso')),
                ('cronometro_aparte', models.TimeField(blank=True, null=True, verbose_name='Cronômetro do Aparte')),
                ('cronometro_ordem', models.TimeField(blank=True, null=True, verbose_name='Cronômetro da Ordem')),
            ],
            options={
                'permissions': (('menu_sistemas', 'Renderizar Menu Sistemas'), ('view_tabelas_auxiliares', 'Visualizar Tabelas Auxiliares')),
                'verbose_name': 'Configurações da Aplicação',
                'verbose_name_plural': 'Configurações da Aplicação',
            },
        ),
        migrations.CreateModel(
            name='Autor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('nome', models.CharField(blank=True, max_length=50, verbose_name='Nome do Autor')),
                ('cargo', models.CharField(blank=True, max_length=50)),
                ('content_type', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Autor',
                'verbose_name_plural': 'Autores',
            },
        ),
        migrations.CreateModel(
            name='CasaLegislativa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=100, verbose_name='Codigo')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome')),
                ('sigla', models.CharField(max_length=100, verbose_name='Sigla')),
                ('endereco', models.CharField(max_length=100, verbose_name='Endereço')),
                ('cep', models.CharField(max_length=100, verbose_name='CEP')),
                ('municipio', models.CharField(max_length=100, verbose_name='Município')),
                ('uf', models.CharField(choices=[('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PR', 'Paraná'), ('PB', 'Paraíba'), ('PA', 'Pará'), ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SE', 'Sergipe'), ('SP', 'São Paulo'), ('TO', 'Tocantins'), ('EX', 'Exterior')], max_length=100, verbose_name='UF')),
                ('telefone', models.CharField(blank=True, max_length=100, verbose_name='Telefone')),
                ('fax', models.CharField(blank=True, max_length=100, verbose_name='Fax')),
                ('logotipo', models.ImageField(blank=True, upload_to='sapl/casa/logotipo/', verbose_name='Logotipo')),
                ('endereco_web', models.URLField(blank=True, max_length=100, verbose_name='HomePage')),
                ('email', models.EmailField(blank=True, max_length=100, verbose_name='E-mail')),
                ('informacao_geral', models.TextField(blank=True, max_length=100, verbose_name='Informação Geral')),
            ],
            options={
                'verbose_name': 'Casa Legislativa',
                'verbose_name_plural': 'Casa Legislativa',
            },
        ),
        migrations.CreateModel(
            name='ProblemaMigracao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(verbose_name='ID do Objeto')),
                ('nome_campo', models.CharField(blank=True, max_length=100, verbose_name='Nome do(s) Campo(s)')),
                ('problema', models.CharField(max_length=300, verbose_name='Problema')),
                ('descricao', models.CharField(max_length=300, verbose_name='Descrição')),
                ('eh_stub', models.BooleanField(verbose_name='É stub?')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='Tipo de Content')),
            ],
            options={
                'verbose_name': 'Problema na Migração',
                'verbose_name_plural': 'Problemas na Migração',
            },
        ),
        migrations.CreateModel(
            name='TipoAutor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=50, verbose_name='Descrição')),
                ('content_type', models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='Modelagem no SAPL')),
            ],
            options={
                'ordering': ['descricao'],
                'verbose_name': 'Tipo de Autor',
                'verbose_name_plural': 'Tipos de Autor',
            },
        ),
        migrations.AddField(
            model_name='autor',
            name='tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.TipoAutor', verbose_name='Tipo do Autor'),
        ),
        migrations.AddField(
            model_name='autor',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='autor',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
