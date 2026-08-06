from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('coming-soon/<str:feature>/', views.coming_soon_view, name='coming_soon'),
]
