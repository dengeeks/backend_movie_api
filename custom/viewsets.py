from rest_framework import views
from rest_framework.viewsets import ViewSetMixin
from custom import generics
from custom import mixins as custom_mixins
from rest_framework import mixins


class CustomGenericViewSet(ViewSetMixin, generics.CustomGenericAPIView):
    """
    The GenericViewSet class does not provide any actions by default,
    but does include the base set of generic view behavior, such as
    the `get_object` and `get_queryset` methods.
    """
    pass


class CustomReadOnlyModelViewSet(mixins.RetrieveModelMixin,
                                 mixins.ListModelMixin,
                                 CustomGenericViewSet):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """
    pass


class CustomModelViewSet(custom_mixins.CustomCreateModelMixin,
                   mixins.RetrieveModelMixin,
                   custom_mixins.CustomUpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   CustomGenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass
