from rest_framework import serializers
from django.db import models


class CustomSerializer(serializers.Serializer):
    def primivive_validated(self):
        return {key: value for key, value in self.validated_data.items() if
                isinstance(value, (int, float, bool, str))}

    def m2m_validated_field(self):
        return {key: value for key, value in self.validated_data.items() if
                isinstance(value, models.ManyToManyField)}
