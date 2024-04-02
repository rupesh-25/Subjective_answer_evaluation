from django.urls import path
from . import views

urlpatterns = [
    path('', views.home,name="home"),
    path('create_vector_db/', views.create_vector_db, name='create_vector_db'),
    path('process/', views.process, name='process'),
]