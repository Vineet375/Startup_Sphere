from django.urls import path
from . import views

app_name = 'incubator'

urlpatterns = [
    path('register/', views.register_startup, name='register_startup'),
]
