from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('graph', views.graph, name='graph'),
    path('fetchAppOptions', views.fetchAppOptions, name='fetchAppOptions'),
    path('example', views.example, name='example'),
    path('appLog', views.appLog, name='appLog'),
    path('run', views.run, name='run'),
]