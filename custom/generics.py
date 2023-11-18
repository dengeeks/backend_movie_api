from django.db.models.query import QuerySet
from rest_framework import mixins, views
from rest_framework.generics import get_object_or_404
from rest_framework.settings import api_settings
from custom import mixins as custom_mixins
from django.db import models



class CustomGenericAPIView(views.APIView):
    """
    Base class for all other generic views.
    """
    queryset = None
    list_serializer_class = None
    create_serializer_class = None
    update_serializer_class = None
    retrieve_serializer_class = None
    lookup_field = 'pk'
    lookup_url_kwarg = None
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    prefetch = None
    select = None

    def get_queryset(self):
        """
        Get the list of items for this view.
        This must be an iterable, and may be a queryset.
        Defaults to using `self.queryset`.

        This method should always be used rather than accessing `self.queryset`
        directly, as `self.queryset` gets evaluated only once, and those results
        are cached for all subsequent requests.

        You may want to override this if you need to provide different
        querysets depending on the incoming request.

        (Eg. return a list of items that is specific to the user)
        """
        assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method."
                % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def get_model_of_queryset(self):
        """return model of queryset"""

        assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method."
                % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, models.Model):
            return queryset
        else:
            return queryset.model

    def get_or_check_m2m_fields(self):
        return self.get_model_of_queryset()._meta.many_to_many

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        method_serializer_map = {
            'POST': self.create_serializer_class,
            'GET': self.retrieve_serializer_class if self.lookup_field in self.kwargs else self.list_serializer_class,
            'PUT': self.update_serializer_class,
            'PATCH': self.update_serializer_class,
        }

        # Проверяем, что для текущего метода у вас есть установленный сериализатор
        current_method = self.request.method
        assert method_serializer_map.get(current_method) is not None, (
            f"No serializer set for method '{current_method}' in '{self.__class__.__name__}'."
        )

        return method_serializer_map[current_method]

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def filter_queryset(self, queryset):
        """
        Given a queryset, filter it with whichever filter backend is in use.

        You are unlikely to want to override this method, although you may need
        to call it either from a list view, or from a custom `get_object`
        method if you want to apply the configured filtering backend to the
        default queryset.
        """
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


class CustomCreateAPIView(mixins.CreateModelMixin,
                          CustomGenericAPIView):
    """
    Concrete view for creating a model instance.
    """

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CustomListApiView(mixins.ListModelMixin, CustomGenericAPIView):
    def get(self, request, *args, **kwargs):
        """Concrete view for listing a queryset."""
        return self.list(request, args, kwargs)


class CustomListCreateApiView(mixins.ListModelMixin, custom_mixins.CustomCreateModelMixin,
                              CustomGenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CustomRetrieveAPIView(mixins.RetrieveModelMixin,
                            CustomGenericAPIView):
    """
    Concrete view for retrieving a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class CustomUpdateAPIView(custom_mixins.CustomUpdateModelMixin,
                          CustomGenericAPIView):
    """
    Concrete view for updating a model instance.
    """

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class CustomDestroyAPIView(mixins.DestroyModelMixin,
                           CustomGenericAPIView):
    """
    Concrete view for deleting a model instance.
    """

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CustomRetrieveUpdateAPIView(mixins.RetrieveModelMixin,
                                  custom_mixins.CustomUpdateModelMixin,
                                  CustomGenericAPIView):
    """
    Concrete view for retrieving, updating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class CustomRetrieveUpdateDestroyAPIView(mixins.RetrieveModelMixin,
                                         custom_mixins.CustomUpdateModelMixin,
                                         mixins.DestroyModelMixin,
                                         CustomGenericAPIView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrieveDestroyAPIView(mixins.RetrieveModelMixin,
                             mixins.DestroyModelMixin,
                             CustomGenericAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
