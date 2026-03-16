from django.urls import path
from . import views

from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.public_schedule, name='public_schedule'),
    path('admin-panel/', views.schedule_list, name='schedule_list'),
    path('schedule/add/', views.schedule_add, name='schedule_add'),
    path('schedule/edit/<int:pk>/', views.schedule_edit, name='schedule_edit'),
    path('schedule/delete/<int:pk>/', views.schedule_delete, name='schedule_delete'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/edit/<int:pk>/', views.teacher_edit, name='teacher_edit'),
    path('teachers/delete/<int:pk>/', views.teacher_delete, name='teacher_delete'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/edit/<int:pk>/', views.subject_edit, name='subject_edit'),
    path('subjects/delete/<int:pk>/', views.subject_delete, name='subject_delete'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/edit/<int:pk>/', views.group_edit, name='group_edit'),
    path('groups/delete/<int:pk>/', views.group_delete, name='group_delete'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
