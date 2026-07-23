from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-job/', views.add_job, name='add_job'),
    path('upload-cv/', views.upload_cv, name='upload_cv'),
    path('candidate/<int:pk>/', views.candidate_detail, name='candidate_detail'),
    path('candidate/<int:pk>/update-status/', views.update_status, name='update_status'),
]