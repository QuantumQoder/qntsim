from rest_framework import serializers
import inspect
from scipy.optimize import minimize
signature = inspect.signature(minimize)

class VQESerializer(serializers.Serializer):
    ansatz = serializers.DictField()
    expectation = serializers.DictField()
    optimizer_details = serializers.DictField()
    num_layers = serializers.IntegerField()


    def validate_optimizer_details(self, optimizer_details):
        # Ensure that 'optimizer_details' is a dictionary
        if not isinstance(optimizer_details, dict):
            raise serializers.ValidationError("Optimizer details must be a dictionary")

        keys = list(optimizer_details.keys())
        param_names = [param_name for param_name in signature.parameters]
        filtered_list = [item for item in param_names if item not in ["fun", "x0", "options", "method"]] + ["maxiter", "disp", "optimizer"]
        unnecessary_elements = [item for item in keys if item not in filtered_list]
        if unnecessary_elements:
            raise serializers.ValidationError(str(unnecessary_elements)+" attributes are not supported")
       
        return optimizer_details


class QAOASerializer(serializers.Serializer):
    initialization = serializers.DictField()
    cost = serializers.DictField()
    mixer = serializers.DictField()
    expectation = serializers.DictField()
    optimizer_details = serializers.DictField()
    num_layers = serializers.IntegerField()

    def validate_optimizer_details(self, optimizer_details):
        # Ensure that 'optimizer_details' is a dictionary
        if not isinstance(optimizer_details, dict):
            raise serializers.ValidationError("Optimizer details must be a dictionary")

        keys = list(optimizer_details.keys())
        param_names = [param_name for param_name in signature.parameters]
        filtered_list = [item for item in param_names if item not in ["fun", "x0", "options", "method"]] + ["maxiter", "disp", "optimizer"]
        unnecessary_elements = [item for item in keys if item not in filtered_list]
        if unnecessary_elements:
            raise serializers.ValidationError(str(unnecessary_elements)+" attributes are not supported")
       
        return optimizer_details
