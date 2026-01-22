from django.urls import path
from . import views

urlpatterns = [
    path("samples/", views.sample_list, name="sample_list"),
    path("samples/new/", views.create_sample, name="create_sample"),  # ← add this
    path("samples/<int:sample_id>/upload/", views.upload_sample_file, name="upload_sample_file"),
    path("search/", views.global_search, name="global_search"),

]

path(
    "samples/<int:sample_id>/generate-str/",
    views.generate_str_from_fastq,
    name="generate_str_from_fastq",
),
