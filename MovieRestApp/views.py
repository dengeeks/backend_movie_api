# from rest_framework.pagination import PageNumberPagination

from django.db import models
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response

from MovieRestApp.models import Movie, Actor
from MovieRestApp.serializers import (MovieListSerializer, MovieDetailSerializer, ReviewCreateSerializer,
                                      CreateRatingSerializer, ActorListSerializer, ActorDetailSerializer)
from MovieRestApp.service import get_client_ip, MovieFilter, PaginationMovies
from django_filters.rest_framework import DjangoFilterBackend


class ActorViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Actor.objects.all()
        serializer = ActorListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, id=None):
        actor = Actor.objects.get(id=id)
        serializer = ActorDetailSerializer(actor)
        return Response(serializer.data)




# class MovieModelViewSet(CustomModelViewSet):
#     lookup_field = 'id'
#     list_serializer_class = MovieListSerializer
#     queryset = Movie.objects.all()


class MovieModelViewSet(viewsets.ReadOnlyModelViewSet):
    """Вывод список фильмов"""
    pagination_class = PaginationMovies
    # serializer_class = MovieListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MovieFilter
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        С помощью annotate добавляем поле
        rating_user = (оставил ли отзыв на фильм)
        middle_star = (Средняя оценка)
        """
        movies = Movie.objects.filter(draft=1).annotate(
            rating_user=models.Count('ratings', filter=models.Q(ratings__ip=get_client_ip(self.request)))
        ).annotate(
            middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
        )
        return movies
    def get_serializer_class(self):
        if self.action == 'list':
            return MovieListSerializer
        elif self.action == 'retrieve':
            return MovieDetailSerializer



# class MovieDetailView(generics.RetrieveAPIView):
#     """Вывод деталей фильмов"""
#
#     queryset = Movie.objects.filter(draft=1)
#     retrieve_serializer_class = MovieDetailSerializer
#     lookup_field = 'id'


class ReviewCreateViewSet(viewsets.ModelViewSet):
    """Добавление отзывов к фильму"""
    serializer_class = ReviewCreateSerializer


class AddStarRatingViewSet(viewsets.ModelViewSet):
    """Добавление звезд фильму"""
    serializer_class = CreateRatingSerializer

    def perform_create(self, serializer):
        """Метод для установки дополнительных полей"""
        serializer.save(ip=(get_client_ip(self.request)))


# class ActorsListView(generics.ListAPIView):
#     """Вывод списка актеров"""
#     queryset = Actor.objects.all()
#     serializer_class = ActorListSerializer
#
#
# class ActorsDetailView(generics.RetrieveAPIView):
#     """Вывод деталей актеров или режиссеров"""
#     queryset = Actor.objects.all()
#     serializer_class = ActorDetailSerializer
#     lookup_field = 'id'
