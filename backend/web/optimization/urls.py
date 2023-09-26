from django.contrib import admin
from django.urls import path
from optimization.views import CircuitVisualizer,RunVQE, RunQAOA
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [

        path('visualization/',CircuitVisualizer.as_view()),
        path('optimization/vqe/',RunVQE.as_view()),
        path('optimization/qaoa/',RunQAOA.as_view())

]