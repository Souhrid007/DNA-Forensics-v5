from django.urls import path
from . import views

urlpatterns = [
    path(
        "reports/generate/<int:query_sample_id>/<int:target_sample_id>/",
        views.generate_report_view,
        name="generate_report",
    ),
]
