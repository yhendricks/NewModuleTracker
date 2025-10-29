from django.urls import path
from . import views

urlpatterns = [
    path('', views.pcb_type_list, name='pcb_type_list'),
    path('create/', views.pcb_type_create, name='pcb_type_create'),
    path('update/<int:pk>/', views.pcb_type_update, name='pcb_type_update'),
    path('delete/<int:pk>/', views.pcb_type_delete, name='pcb_type_delete'),
    path('<int:pk>/', views.pcb_type_detail, name='pcb_type_detail'),
]