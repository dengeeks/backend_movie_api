from rest_framework.response import Response
from rest_framework import status
from rest_framework.settings import api_settings


class CustomCreateModelMixin:
    """
    Create a model instance.
    """

    def create(self, request, *args, **kwargs):
        model = self.get_model_of_queryset()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = model.objects.create(**serializer.primivive_validated())
        if serializer.m2m_validated_field():
            for key, value in serializer.m2m_validated_field().items():
                getattr(instance, key).set(value)
        self.perform_create(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, instance):
        instance.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class CustomUpdateModelMixin:
    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if serializer.primivive_validated():
            instance.__dict__.update(**serializer.primivive_validated())
        if serializer.m2m_validated_field():
            for key, value in serializer.non_primitive().items():
                getattr(instance, key).set(value)
        self.perform_update(instance)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, instance):
        instance.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
