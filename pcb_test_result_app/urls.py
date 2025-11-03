from django.urls import path
from . import views

urlpatterns = [
    path('', views.pcb_test_result_list, name='pcb_test_result_list'),
    path('create/', views.pcb_test_result_create, name='pcb_test_result_create'),
    path('execute/<int:pcb_id>/', views.pcb_test_execute_steps, name='pcb_test_execute_steps'),
    path('complete/<int:pk>/', views.pcb_test_complete, name='pcb_test_result_complete'),
    path('pcb/<str:pcb_serial_number>/', views.pcb_test_results_by_pcb, name='pcb_test_results_by_pcb'),
    path('<int:pk>/', views.pcb_test_result_detail, name='pcb_test_result_detail'),
    path('update/<int:pk>/', views.pcb_test_result_update, name='pcb_test_result_update'),
    path('delete/<int:pk>/', views.pcb_test_result_delete, name='pcb_test_result_delete'),
]