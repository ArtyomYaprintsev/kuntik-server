from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet, ModelViewSet


from store import models, serializers
from store.permissions import IsAuthenticatedOrListOnlyPermission


class ColorViewSet(ModelViewSet):
    lookup_field = 'name'

    queryset = models.Color.objects.all()
    serializer_class = serializers.ColorSerializer
    permission_classes = (IsAuthenticatedOrListOnlyPermission, )


class MaterialViewSet(ModelViewSet):
    lookup_field = "name"

    queryset = models.Material.objects.all()
    serializer_class = serializers.MaterialSerializer
    permission_classes = (IsAuthenticatedOrListOnlyPermission, )
