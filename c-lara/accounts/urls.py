from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('game/', views.game_view, name='game'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('results/summary/', views.results_summary, name='summary'),
    path('results/statistics/', views.results_statistics, name='statistics'),
    path('about/', views.about, name='about'),
    path('logout/', views.logout_view, name='logout'),
    path('summary/', views.summary_view, name='summary')
]
