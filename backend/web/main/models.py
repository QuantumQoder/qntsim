from email.policy import default
from django.db import models
from users.models import CustomUser
from django.contrib.postgres.fields import ArrayField
# Create your models here.

class Applications(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    
    def __str__(self):
        return self.name

class Results(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    input = models.JSONField(default = list)
    topology = models.JSONField(default = list)
    output = models.JSONField(default = list, null = True, blank =True)
    logs = models.TextField(null = True, blank =True)
    graphs = models.JSONField(default = list,null = True, blank =True)
    app_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

# class CircuitModel(models.Model):
#     circuit_id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=200)
#     description = models.CharField(max_length=1000)
    
# class Layers(models.Model):
#     layer_id = models.AutoField(primary_key=True)
#     circuit_id = models.ForeignKey(CircuitModel, on_delete=models.CASCADE)
#     layer_name = models.CharField(max_length=200)
#     layer_description = models.CharField(max_length=1000)

# class GateTypes(models.Model):
#     gt_id = models.AutoField(primary_key=True)
#     gt_name = models.CharField(max_length=200)
#     single_multiple = models.CharField(max_length=10)
#     gt_description = models.CharField(max_length=1000)

# class Gates(models.Model):
#     gate_id = models.AutoField(primary_key=True)
    
#     gate_name = models.CharField(max_length=200)
#     gate_description = models.CharField(max_length=1000)

# class LayerGates(models.Model):
#     layer_gate_id = models.AutoField(primary_key=True)
#     circuit_id = models.ForeignKey(CircuitModel, on_delete=models.CASCADE)
#     layer_id = models.ForeignKey(Layers, on_delete=models.CASCADE)
#     gate_id = models.ForeignKey(Gates, on_delete=models.CASCADE)
#     gate_inputs = ArrayField(models.CharField(max_length=512),default=list)
    
    