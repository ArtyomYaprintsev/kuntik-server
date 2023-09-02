from rest_framework import serializers

from store import models


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Color
        fields = "__all__"


class RetrieveColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Color
        fields = ("id", "name", )


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Material
        fields = "__all__"


class RetrieveMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Material
        fields = ("id", "name", )


class PreparedPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PreparedPurchase
        fields = "__all__"


class AbstractReadOnlyPurchaseSerializerMixin:
    color = RetrieveColorSerializer()
    material = RetrieveMaterialSerializer()
    size = serializers.ChoiceField(
        choices=models.PreparedPurchase.Size.choices,
        source="get_size_display",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self.Meta, 'read_only_fields', [*self.fields])


class ReadOnlyPreparedPurchaseSerializer(
    AbstractReadOnlyPurchaseSerializerMixin,
    serializers.ModelSerializer,
):
    class Meta:
        model = models.PreparedPurchase
        fields = (
            "id", "title", "description",
            "color", "material", "size",
            "weight", "price", "delivery_type",
        )


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Purchase
        fields = "__all__"


class ReadOnlyPurchaseSerializer(
    AbstractReadOnlyPurchaseSerializerMixin,
    serializers.ModelSerializer,
):
    class Meta:
        model = models.Purchase
        fields = (
            "code",
            "color", "material", "size",
            "weight", "price", "delivery_type",
            "state", "address",
            # "is_prepared", # For authenticated users
            "date_created", "date_updated",
        )


class ConsultSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Consult
        fields = "__all__"
