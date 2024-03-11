"""volunteers_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('api/user-profile/<telegram_user_id>', views.UserProfileAPIView.as_view()),
    path('api/links/<telegram_user_id>/<offset>', views.UserWorkListAPIView.as_view()),
    path('api/tasks/<telegram_user_id>', views.TaskListAPIView.as_view()),
    path('api/send_link/', views.UserWorkCreateAPIView.as_view()),
    path('api/auth/verify/', views.VerifyAPIView.as_view()),
    path('api/auth/signin/', views.LoginAPIView.as_view()),
    path('api/rating/', views.RatingAPIView.as_view()),
    path('api/tasks/new/', views.UserTaskCreateAPIView.as_view()),
    path('api/tasks/update/', views.UserTaskUpdateAPIView.as_view()),
    path('api/user_tasks/<telegram_user_id>', views.UserTaskListAPIView.as_view()),
]
