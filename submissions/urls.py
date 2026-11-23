from django.urls import path

from . import views

app_name = 'submissions'

urlpatterns = [
    path('<slug:slug>/submit/', views.submit_code, name='submit'),
    path('report/<int:pk>/', views.submission_report, name='report'),
    path('<slug:slug>/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
]
