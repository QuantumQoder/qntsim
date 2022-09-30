from dataclasses import fields
from simulator.models import Applications
from rest_framework import serializers

class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Applications
        fields = "__all__"