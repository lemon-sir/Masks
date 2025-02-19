from django.urls import path
from . import views

app_name = 'masks'

urlpatterns = [
    path('', views.compare_masks, name='compare_masks'),
] 