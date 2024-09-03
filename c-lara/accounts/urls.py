from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Mapping root URL to home_view
    path('login/', views.login_view, name='login'),  # Mapping URL to login_view
]
