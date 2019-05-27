from rest_framework.viewsets import ReadOnlyModelViewSet

from areas.models import Areas
from areas.serializer import AreasSerializer, SubsSerializer
from rest_framework_extensions.cache.mixins import CacheResponseMixin


# noinspection PyUnresolvedReferences
class AreasViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    """序列化市区县"""
    pagination_class = None

    def get_queryset(self):
        if self.action == "list":
            return Areas.objects.filter(parent=None)
        return Areas.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AreasSerializer
        return SubsSerializer
