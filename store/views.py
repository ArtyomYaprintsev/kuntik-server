from django.http import Http404

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from store import models, serializers, permissions, pagination


class ColorViewSet(ModelViewSet):
    """`ModelViewSet` for `store.models.Color` model."""

    lookup_field = 'name'

    queryset = models.Color.objects.all()
    serializer_class = serializers.ColorSerializer
    permission_classes = (permissions.IsAuthenticatedOrListOnlyPermission, )


class MaterialViewSet(ModelViewSet):
    """`ModelViewSet` for `store.models.Material` model."""

    lookup_field = "name"

    queryset = models.Material.objects.all()
    serializer_class = serializers.MaterialSerializer
    permission_classes = (permissions.IsAuthenticatedOrListOnlyPermission, )


class PreparedPurchaseViewSet(ModelViewSet):
    """`ModelViewSet` for `store.models.PreparedPurchase` model."""

    queryset = models.PreparedPurchase.objects.all()
    serializer_class = serializers.PreparedPurchaseSerializer
    permission_classes = (permissions.IsAuthenticatedOrListOnlyPermission, )
    pagination_class = pagination.StandardPageNumberPagination

    def get_serializer_class(self):
        """Return read only serializer for the `GET` method."""

        if self.action in ["list", "retrieve"]:
            return serializers.ReadOnlyPreparedPurchaseSerializer

        return super().get_serializer_class()


class PurchaseViewSet(ModelViewSet):
    """`ModelViewSet` for `store.models.Purchase` model."""

    lookup_field = "code"

    queryset = models.Purchase.objects.all()
    serializer_class = serializers.PurchaseSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrCreateRetrievePermission,
    )
    pagination_class = pagination.StandardPageNumberPagination

    def get_serializer_class(self):
        """Return read only serializer for the `GET` method."""

        if self.action in ["list", "retrieve"]:
            return serializers.ReadOnlyPurchaseSerializer

        return super().get_serializer_class()

    @action(
        methods=["GET", "PUT", "PATCH", "HEAD", "OPTIONS"],
        detail=True, url_name="purchase-consult",
        serializer_class=serializers.ConsultSerializer,
        permission_classes=(IsAuthenticated, ),
    )
    def consult_view(self, request, code=None, format=None):
        """View for manage related `Consult` instance.

        Raises:
            Http404: if the related `Consult` instance does not exist.

        """
        instance = self.get_object()
        consult = getattr(instance, "consult", None)

        if consult is None:
            raise Http404

        if request.method in ["HEAD", "OPTIONS"]:
            meta = self.metadata_class()
            data = meta.determine_metadata(request, self)
            return Response(data)

        if request.method == "GET":
            serializer = self.get_serializer(consult)

            return Response(serializer.data)

        if request.method in ["PUT", "PATCH"]:
            partial = request.method == "PATCH"

            serializer = self.get_serializer(
                instance, data=request.data, partial=partial,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
