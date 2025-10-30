from django.urls import path
from . import views

urlpatterns = [
    path('', views.batch_list, name='batch_list'),
    path('create/', views.batch_create, name='batch_create'),
    path('update/<int:pk>/', views.batch_update, name='batch_update'),
    path('delete/<int:pk>/', views.batch_delete, name='batch_delete'),
    path('pcb/create/', views.batch_pcb_create, name='batch_pcb_create'),
    path('pcb/delete/<int:pcb_id>/', views.batch_pcb_delete, name='batch_pcb_delete'),
    path('<int:pk>/', views.batch_detail, name='batch_detail'),
]