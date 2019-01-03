from datetime import datetime
import os

from django.utils.timezone import make_aware
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.templatetags.thumbnail import thumbnail
from rest_framework import serializers
from rest_framework.relations import StringRelatedField

from sapl.base.models import Autor
from sapl.materia.models import MateriaLegislativa, Anexada, Autoria,\
    DocumentoAcessorio, Tramitacao
from sapl.norma.models import NormaJuridica, LegislacaoCitada
from sapl.parlamentares.models import Parlamentar
from sapl.sessao.models import SessaoPlenaria, OrdemDia, ExpedienteMateria,\
    RegistroVotacao


class IntRelatedField(StringRelatedField):
    def to_representation(self, value):
        return int(value)


class SessaoPlenariaSerializer(serializers.ModelSerializer):
    sessao_legislativa = IntRelatedField(source="sessao_legislativa.numero")
    legislatura = IntRelatedField(source="legislatura.numero")
    tipo = serializers.StringRelatedField()

    class Meta:
        model = SessaoPlenaria
        fields = ('id',
                  'sessao_legislativa',
                  'legislatura',
                  'tipo',
                  'data_inicio',
                  'data_fim',
                  'hora_inicio',
                  'hora_fim',
                  'numero',)


class AutorSerializer(serializers.ModelSerializer):
    fotografia = serializers.SerializerMethodField()
    file_date_updated = serializers.SerializerMethodField()

    class Meta:
        model = Autor
        fields = ('id', 'nome', 'fotografia', 'file_date_updated')

    def thumbnail(self, obj):

        thumb = get_thumbnailer(obj.fotografia)

        return thumb.get_thumbnail({
            'size': (128, 128),
            'box':  obj.cropping,
            'crop': True,
            'detail': True,
        })

    def get_fotografia(self, obj):
        try:
            if isinstance(obj, Autor):
                obj = obj.autor_related
            if obj:
                if hasattr(obj, 'fotografia'):
                    return self.thumbnail(obj).url

        except:
            return ''
        return ''

    def get_file_date_updated(self, obj):
        if isinstance(obj, Autor):
            obj = obj.autor_related
        if obj:
            if hasattr(obj, 'fotografia'):
                file = obj.fotografia
                try:
                    thumbnail = self.thumbnail(obj)
                    path = file.path.split("/")
                    path[-1] = thumbnail.name.split("/")[-1]
                    path = "/".join(path)
                    lastmodified = os.stat(path).st_mtime

                    return make_aware(datetime.utcfromtimestamp(
                        lastmodified)).isoformat(timespec='milliseconds')[:-6]
                except:
                    return None
        return None


class AutoriaSerializer(serializers.ModelSerializer):
    autor = AutorSerializer()

    class Meta:
        model = Autoria
        fields = '__all__'


class AutorParlamentarSerializer(AutorSerializer):
    nome = serializers.CharField(source="nome_parlamentar")

    class Meta(AutorSerializer.Meta):
        model = Parlamentar


class DocumentoAcessorioSerializer(serializers.ModelSerializer):
    tipo = serializers.StringRelatedField(many=False)
    arquivo = serializers.SerializerMethodField()
    file_date_updated = serializers.SerializerMethodField()

    class Meta:
        model = DocumentoAcessorio
        fields = ('id',
                  'tipo',
                  'arquivo',
                  'nome',
                  'data',
                  'autor',
                  'ementa',
                  'indexacao',
                  'materia',
                  'file_date_updated'
                  )

    def get_arquivo(self, obj):
        return obj.arquivo.url

    def get_file_date_updated(self, obj):
        file = obj.arquivo
        try:
            lastmodified = os.stat(file.path).st_mtime
            return make_aware(
                datetime.utcfromtimestamp(lastmodified)
            ).isoformat(timespec='milliseconds')[:-6]
        except:
            return None


class MateriaLegislativaSerializerMixin(serializers.ModelSerializer):
    tipo = serializers.StringRelatedField(many=False)
    tipo_sigla = serializers.SerializerMethodField()
    file_date_updated = serializers.SerializerMethodField()
    autoria = AutoriaSerializer(
        many=True, source='autoria_set', read_only=True)

    documentos_acessorios = DocumentoAcessorioSerializer(
        many=True, source='documentoacessorio_set', read_only=True)
    texto_original = serializers.SerializerMethodField()

    class Meta:
        model = MateriaLegislativa
        fields = ('id',
                  'tipo',
                  'tipo_sigla',
                  'numero',
                  'ano',
                  'numero_protocolo',
                  'data_apresentacao',
                  'ementa',
                  'texto_original',
                  'autoria',
                  'file_date_updated',
                  'documentos_acessorios'
                  )

    def get_tipo_sigla(self, obj):
        return obj.tipo.sigla

    def get_texto_original(self, obj):
        if obj.texto_original:
            return obj.texto_original.url
        return ''

    def get_file_date_updated(self, obj):
        file = obj.texto_original
        try:
            lastmodified = os.stat(file.path).st_mtime
            return make_aware(
                datetime.utcfromtimestamp(lastmodified)
            ).isoformat(timespec='milliseconds')[:-6]
        except:
            return None


class MateriaAnexadaSerializer(serializers.ModelSerializer):
    materia_anexada = MateriaLegislativaSerializerMixin()

    class Meta:
        model = Anexada
        fields = '__all__'


class MateriaPrincipalSerializer(serializers.ModelSerializer):
    materia_principal = MateriaLegislativaSerializerMixin()

    class Meta:
        model = Anexada
        fields = '__all__'


class MateriaLegislativaSerializer(MateriaLegislativaSerializerMixin):
    anexadas = MateriaAnexadaSerializer(many=True, read_only=True,
                                        source='materia_principal_set')

    anexo_de = MateriaPrincipalSerializer(many=True, read_only=True,
                                          source='materia_anexada_set')

    #anexadas = MateriaLegislativaSerializerMixin(many=True)
    #anexo_de = MateriaLegislativaSerializerMixin(many=True)

    class Meta(MateriaLegislativaSerializerMixin.Meta):

        fields = ('id',
                  'tipo',
                  'tipo_sigla',
                  'numero',
                  'ano',
                  'numero_protocolo',
                  'data_apresentacao',
                  'ementa',
                  'texto_original',
                  'anexadas',
                  'anexo_de',
                  'autoria',
                  'file_date_updated',
                  'documentos_acessorios'
                  )


class TramitacaoSerializer(serializers.ModelSerializer):
    status = StringRelatedField()
    unidade_tramitacao_local = StringRelatedField()
    unidade_tramitacao_destino = StringRelatedField()

    class Meta:
        model = Tramitacao
        fields = (
            'id',
            'data_tramitacao',
            'texto',
            'status',
            'materia',
            'unidade_tramitacao_local',
            'unidade_tramitacao_destino'
        )


class NormaJuridicaSerializer(serializers.ModelSerializer):
    tipo = serializers.StringRelatedField()

    class Meta:
        model = NormaJuridica
        fields = ('id',
                  'numero',
                  'ano',
                  'data',
                  'data_publicacao',
                  'ementa',
                  'tipo',
                  )


class LegislacaoCitadaSerializer(serializers.ModelSerializer):

    class Meta:
        model = LegislacaoCitada
        fields = ('id',
                  'materia',
                  'norma'
                  )


class RegistroVotacaoSerializer(serializers.ModelSerializer):
    tipo_resultado_votacao = StringRelatedField()

    class Meta:
        model = RegistroVotacao
        fields = '__all__'


class SessaoSerializerMixin(serializers.ModelSerializer):
    votacao = RegistroVotacaoSerializer(
        many=True, source='registrovotacao_set')

    class Meta:
        fields = ('id',
                  'materia',
                  'observacao',
                  'numero_ordem',
                  'resultado',
                  'tipo_votacao',
                  'sessao_plenaria',
                  'votacao')


class ExpedienteMateriaSerializer(SessaoSerializerMixin):
    class Meta(SessaoSerializerMixin.Meta):
        model = ExpedienteMateria


class OrdemDiaSerializer(SessaoSerializerMixin):
    class Meta(SessaoSerializerMixin.Meta):
        model = OrdemDia
