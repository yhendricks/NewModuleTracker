from django.urls import path
from . import views

urlpatterns = [
    path('', views.module_config_type_list, name='module_config_type_list'),
    path('create/', views.module_config_type_create, name='module_config_type_create'),
    path('update/<int:pk>/', views.module_config_type_update, name='module_config_type_update'),
    path('delete/<int:pk>/', views.module_config_type_delete, name='module_config_type_delete'),
    path('<int:pk>/', views.module_config_type_detail, name='module_config_type_detail'),
]
