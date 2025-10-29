from django.urls import path
from . import views

urlpatterns = [
    path('', views.test_config_type_list, name='test_config_type_list'),
    path('create/', views.test_config_type_create, name='test_config_type_create'),
    path('update/<int:pk>/', views.test_config_type_update, name='test_config_type_update'),
    path('delete/<int:pk>/', views.test_config_type_delete, name='test_config_type_delete'),
    path('<int:pk>/', views.test_config_type_detail, name='test_config_type_detail'),
]