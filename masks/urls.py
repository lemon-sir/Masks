from django.urls import path
from . import views

app_name = 'masks'

urlpatterns = [
    path('', views.compare_masks, name='compare_masks'),
    path('upload/', views.upload_image, name='upload_image'),
] 