from django.urls import path
from .views import index, download_csv

urlpatterns = [
    path('', index, name='index'),
    path('download_csv/', download_csv, name='download_csv'),
]