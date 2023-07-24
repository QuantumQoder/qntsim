from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('apps', views.apps, name='apps'),
    path('graph', views.graph, name='graph'),
    path('fetchAppOptions', views.fetchAppOptions, name='fetchAppOptions'),
    path('appLog', views.appLog, name='appLog'),
    path('run', views.run, name='run'),
]