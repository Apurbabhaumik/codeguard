from django.urls import path

from . import views

app_name = 'assignments'

urlpatterns = [
    path('', views.AssignmentListView.as_view(), name='list'),
    path('new/', views.AssignmentCreateView.as_view(), name='create'),
    path('<slug:slug>/', views.assignment_detail, name='detail'),
]
