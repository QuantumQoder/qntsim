from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('makeGraph', views.makeGraph, name='makeGraph'),
    path('graph', views.graph, name='graph'),
]