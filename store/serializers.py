from rest_framework import serializers

from store import models


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Color
        fields = "__all__"


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Material
        fields = "__all__"
