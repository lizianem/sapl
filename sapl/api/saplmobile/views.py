
from datetime import datetime
from django import apps
from django.conf import settings
from django.db.models import Q
from django.utils.decorators import classonlymethod
from django.utils.timezone import utc
from rest_framework import serializers as rest_serializers
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from reversion.models import Version

from sapl.api.saplmobile.serializers import AutorParlamentarSerializer
from sapl.base.models import Autor
from sapl.materia.models import MateriaLegislativa, Anexada, Autoria,\
    DocumentoAcessorio, Tramitacao
from sapl.norma.models import NormaJuridica, LegislacaoCitada
from sapl.parlamentares.models import Parlamentar
from sapl.sessao.models import SessaoPlenaria, ExpedienteMateria, OrdemDia,\
    RegistroVotacao


def _get_registration_key(model):
    return '%s:%s' % (model._meta.app_label, model._meta.model_name)


def __time_refresh_generate():

    from django.contrib.contenttypes.models import ContentType
    result = {}
    apps_sapl = [apps.apps.get_app_config(n[5:]) for n in settings.SAPL_APPS]

    for app in apps_sapl:
        for model in app.get_models():
            ct = ContentType.objects.get_for_model(model)
            result[ct.id] = _get_registration_key(model)

    return result


_time_refresh_models = {}


def time_refresh_models():
    if not _time_refresh_models:
        _time_refresh_models.update(__time_refresh_generate())
    return _time_refresh_models


class TimeRefreshDatabaseView(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        data = request.query_params.get('date', None)

        q = Q()
        if data:
            data = datetime.strptime(data, '%Y-%m-%dT%H:%M:%S.%f')
            data = data.replace(tzinfo=utc)
            q &= Q(revision__date_created__gte=data)

        versions = Version.objects.filter(q).order_by(
            'content_type_id',
            '-revision__date_created'
        ).values_list(
            'content_type_id',
            'revision__date_created'
        ).distinct('content_type_id')

        times = {}
        for vs in versions:
            times[time_refresh_models()[vs[0]]] = vs[1].isoformat(
                timespec='milliseconds')[:-6]

        return Response(times)


class TimeRefreshMobileMixin(ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    deletados = None

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if 'pagination' in response.data:
            response.data['deleted'] = self.deletados if self.deletados and \
                response.data['pagination']['page'] == 1 else []
        return response

    def get_queryset(self):
        return self.queryset_refresh()

    def queryset_refresh(self, queryset=None, **kwargs):

        qs = queryset if queryset else super().get_queryset()
        opts = qs.model._meta

        data_min = self.request.query_params.get(
            'data_min', kwargs.get('data_min', None))
        data_max = self.request.query_params.get(
            'data_max', kwargs.get('data_max', None))
        tipo_update = self.request.query_params.get(
            'tipo_update', kwargs.get('tipo_update', 'get'))
        fk_name = self.request.query_params.get(
            'fk_name', kwargs.get('fk_name', ''))
        fk_pk = self.request.query_params.get(
            'fk_pk', kwargs.get('fk_pk', 0))

        if fk_name:
            qs = qs.filter(**{fk_name: fk_pk})

        if data_min:
            data_min = datetime.strptime(data_min, '%Y-%m-%dT%H:%M:%S.%f')
            data_min = data_min.replace(tzinfo=utc)
        if data_max:
            data_max = datetime.strptime(data_max, '%Y-%m-%dT%H:%M:%S.%f')
            data_max = data_max.replace(tzinfo=utc)

        if data_min or data_max:
            if tipo_update == 'sync':
                q_model = Q(content_type__app_label=opts.app_label,
                            content_type__model=opts.model_name)

                q_data = Q()
                if data_min:
                    q_data &= Q(revision__date_created__gte=data_min)

                if data_max:
                    q_data &= Q(revision__date_created__lte=data_max)

                vs = Version.objects.filter(q_model).order_by(
                    '-revision__date_created', '-object_id')

                vs_sync = vs.filter(q_data).values_list('object_id', flat=True)
                vs_sync = set(map(int, vs_sync))

                # com o código abaixo envia todos os deletados no período sel.
                qs = qs.filter(id__in=vs_sync)
                qs_values = set(qs.values_list('id', flat=True))
                self.deletados = vs_sync - qs_values

                # com código abaixo envia todos os deletados
                # qs_values = set(qs.values_list('id', flat=True))
                # qs = qs.filter(id__in=vs_sync)
                # vs = vs.values_list('object_id', flat=True)
                # vs = set(map(int, vs))
                # self.deletados = vs - qs_values

            elif tipo_update in ('get', 'last_items', 'first_items'):
                """
                    se a data for datetime e o campo DateField
                    as partes de um dia são descartadas no filtro. 
                """
                params = {}
                field_to_filter_date = kwargs.get(
                    'field_to_filter_date', self.field_to_filter_date)

                if field_to_filter_date:
                    if data_min:
                        params['{}__gte'.format(
                            field_to_filter_date[0])] = data_min
                    if data_max:
                        params['{}__lte'.format(
                            field_to_filter_date[0])] = data_max

                qs = qs.filter(**params)

        if tipo_update == 'first_items':
            qs = qs[:self.paginator.page_size]
        elif tipo_update == 'last_items':
            qs = qs[self.paginator.page_size * (-1):]
        elif tipo_update == 'get_initial':
            qs = qs[:self.paginator.page_size]

        return qs

    @classonlymethod
    def build_class(cls, set_description):
        import inspect
        from sapl.api.saplmobile import serializers
        serializers_classes = inspect.getmembers(serializers)
        serializers_classes = {i[0]: i[1] for i in filter(
            lambda x: x[0].endswith('Serializer'),
            serializers_classes
        )}

        built_sets = {}

        def build(_model, _field_to_filter_date=None,
                  _fields='__all__', _serializer_class=None):
            """
                Se _serializer_class not is None e não existe um serializer para
                o model, a função build cria um ModelSerializer com o conteúdo
                de _fields para o _model, porém, com fields não customizaveis
            """

            if not _serializer_class:
                ser_name = '%sSerializer' % _model._meta.object_name

                _serializer_class = serializers_classes.get(
                    ser_name, _serializer_class)

            def create_class():
                class ModelSerializer(rest_serializers.ModelSerializer):
                    class Meta:
                        model = _model
                        fields = _fields

                class ModelTimeRefreshViewSet(cls):
                    queryset = _model.objects.all() \
                        if not _field_to_filter_date else \
                        _model.objects.order_by(
                            *list(
                                map(
                                    lambda x: '-%s' % x,
                                    _field_to_filter_date
                                )
                            )
                    )
                    field_to_filter_date = _field_to_filter_date
                    serializer_class = _serializer_class \
                        if _serializer_class else ModelSerializer

                return ModelTimeRefreshViewSet

            viewset = create_class()
            viewset.__name__ = '%sTimeRefreshViewSet' % _model.__name__
            return viewset

        for app, description_class in set_description.items():
            built_sets[app] = {}
            for description in description_class:
                if isinstance(description, dict):
                    built_sets[app][
                        description['model']._meta.model_name] = build(
                            description['model'],
                            _field_to_filter_date=description.get(
                                'field_to_filter_date', None),
                            _fields=description.get('fields', None),
                            _serializer_class=description.get(
                                'serializer_class', None)
                    )
                else:
                    built_sets[app][description._meta.model_name] = build(
                        description)
        return built_sets


TimeRefreshSetViews = TimeRefreshMobileMixin.build_class(
    set_description={
        'base': [Autor, ],
        'sessao': [
            OrdemDia, ExpedienteMateria, RegistroVotacao,
            {
                'model': SessaoPlenaria,
                'field_to_filter_date': ('data_inicio', 'hora_fim'),
            },
        ],
        'materia': [
            Anexada, Autoria, DocumentoAcessorio, Tramitacao,
            {
                'model': MateriaLegislativa,
                'field_to_filter_date': ('data_apresentacao', ),
            }
        ],
        'norma': [
            NormaJuridica, LegislacaoCitada
        ]
    }
)


class _AutorViewSet(TimeRefreshSetViews['base']['autor']):

    @list_route()
    def parlamentar(self, request, *args, **kwargs):
        qs = Parlamentar.objects.all()
        qs = self.queryset_refresh(qs, field_to_filter_date=None)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = AutorParlamentarSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)


TimeRefreshSetViews['base']['autor'] = _AutorViewSet
