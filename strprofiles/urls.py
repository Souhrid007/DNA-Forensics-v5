from django.urls import path
from . import views

urlpatterns = [
    path("samples/<int:sample_id>/str/upload/", views.upload_str_profile_csv, name="upload_str_csv"),
    path("samples/<int:sample_id>/str/view/", views.view_str_profile, name="view_str_profile"),
]
