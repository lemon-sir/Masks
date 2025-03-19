from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'masks'

urlpatterns = [
    path('', views.compare_masks, name='compare_masks'),
    path('upload/', views.upload_image, name='upload_image'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('user-management/', views.user_management, name='user_management'),
    path('toggle_user_status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('user_history/<int:user_id>/', views.user_history, name='user_history'),
    path('my-history/', views.user_query_history, name='my_history'),
    path('load_history_params/<int:history_id>/', views.load_history_params, name='load_history_params'),
    path('toggle-cloud-member/<int:user_id>/', views.toggle_cloud_member, name='toggle_cloud_member'),
] 