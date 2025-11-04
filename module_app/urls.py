from django.urls import path
from . import views

urlpatterns = [
    path('', views.module_list, name='module_list'),
    path('create/', views.module_create, name='module_create'),
    path('update/<int:pk>/', views.module_update, name='module_update'),
    path('delete/<int:pk>/', views.module_delete, name='module_delete'),
    path('<int:pk>/', views.module_detail, name='module_detail'),
    path('<int:pk>/status/', views.module_status_change, name='module_status_change'),
    path('<int:pk>/add-atp-report/', views.module_add_atp_report, name='module_add_atp_report'),
    path('<int:pk>/add-ess-report/', views.module_add_ess_report, name='module_add_ess_report'),
    path('signoff/<str:report_type>/<int:report_id>/', views.module_signoff_report, name='module_signoff_report'),
]
