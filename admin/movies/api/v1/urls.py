from django.urls import path

from . import views


urlpatterns = [
    path('movies/<uuid:pk>/', views.DetailFilmView.as_view()),
    path('movies/', views.ListFilmView.as_view())
]
