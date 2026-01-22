from django.urls import path
from . import views

urlpatterns = [
    path("matching/compare/", views.compare_samples_view, name="compare_samples"),
    path("matching/search/", views.search_matches_view, name="search_matches"),
]
