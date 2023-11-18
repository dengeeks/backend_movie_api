from django.urls import path
from MovieRestApp import views

urlpatterns = [
    path('movie/', views.MovieModelViewSet.as_view({
        'get': 'list'
    })),
    path('movie/<int:pk>/', views.MovieModelViewSet.as_view({
        'get': 'retrieve'
    })),
    path('review/', views.ReviewCreateViewSet.as_view({
        'post':'create'
    })),
    path('rating/', views.AddStarRatingViewSet.as_view({
        'post':'create'
    })),
    path('actors/', views.ActorViewSet.as_view({
        'get': 'list',
    })),
    path('actors/<int:id>/', views.ActorViewSet.as_view({
        'get': 'retrieve'
    })),
]
