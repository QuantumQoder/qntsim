from optimization.circuit_visualizer import composer
from optimization.vqa import VQA, QAOA
from copy import deepcopy
from rest_framework.views import APIView
from rest_framework import permissions
from django.http import  JsonResponse
from optimization.serializers import VQESerializer, QAOASerializer
import numpy as np

# Create your views here.
class CircuitVisualizer(APIView):

    def post(self,request):
        # //add these lines for apis (APIView)
        authentication_classes = ()
        permission_classes = (permissions.AllowAny,)
        com = composer("in")
        output = com.get_circuit(request.data, flag="visualization")
        return JsonResponse(output, safe = False)

    
    
class RunVQE(APIView):
    

    def post(self,request):
        valid_ser = VQESerializer(data=request.data)
        if valid_ser.is_valid():
            post_data = valid_ser.validated_data
        else:
            print(valid_ser.errors)


        optimizer_details=valid_ser.validate_optimizer_details(request.data["optimizer_details"])

        # authentication_classes = ()
        # permission_classes = (permissions.AllowAny)
        # initialization=request.data["initialization"]#["node1"]
        # com = composer("in")
        # com.get_circuit(deepcopy(initialization))
        # initialization=com.qc
        
        
        ansatz=request.data["ansatz"]#["node1"]
        com = composer("az")
        com.get_circuit(deepcopy(ansatz))
        ansatz=com.qc
        # print("ansatz:", ansatz)
        
        expectation=request.data["expectation"]#["node1"]
        com = composer("ex")
        com.get_circuit(deepcopy(expectation))
        expectation=com.qc
        
        
        vqa = VQA(
                  ansatz=ansatz, 
                  num_layers=1,  
                  expectation=expectation)
        
        
        initial_params=np.random.random(vqa.num_layers*len(vqa.variational_params))
        result,iteration_results = vqa.optimization(args=optimizer_details, initial_params=initial_params)
        output={"fun":result.fun,
         "initial_params":initial_params.tolist(),
         "final_params": result.x.tolist(),
         "graph":iteration_results}
        return JsonResponse(output, safe = False)
    
    
    
class RunQAOA(APIView):

    def post(self,request):
        valid_ser = QAOASerializer(data=request.data)
        if valid_ser.is_valid():
            post_data = valid_ser.validated_data
        else:
            print(valid_ser.errors)
        
        optimizer_details=valid_ser.validate_optimizer_details(request.data["optimizer_details"])

        initialization=request.data["initialization"]#["node1"]
        # print("ini")
        com = composer("in")
        com.get_circuit(deepcopy(initialization))
        initialization=com.qc
        
        # print("costi")
        cost=request.data["cost"]#["node1"]
        com = composer("cm")
        com.get_circuit(deepcopy(cost))
        cost=com.qc
        # print("mixi")
        mixer=request.data["mixer"]#["node1"]
        com = composer("mm")
        com.get_circuit(deepcopy(mixer))
        mixer=com.qc
        # print("expi")
        expectation=request.data["expectation"]#["node1"]
        com = composer("ex")
        com.get_circuit(deepcopy(expectation))
        expectation=com.qc
        
        
        qaoa = QAOA(initialization=initialization,
                  cost=cost,
                  mixer=mixer, 
                  num_layers=request.data["num_layers"],
                  expectation=expectation)


        initial_params = np.random.random(qaoa.num_layers*2)
        result,iteration_results = qaoa.optimization(args=optimizer_details, initial_params=initial_params)
        output={"fun":result.fun,
         "initial_params": initial_params.tolist(),
         "final_params": result.x.tolist(),
         "graph":iteration_results}
        return JsonResponse(output, safe = False)
    
    
# class RunVQC(APIView):

#     def post(self,request):
        
#         vqc = VQC(request.data["feature_map"], request.data["ansatz"])
#         result = vqc.optimization(optimizer=request.data["optimizer"], final_data = request.data["final_data"], lables= request.data["lables"])
#         output={"fun":result.fun}
#         return JsonResponse(output, safe = False)
    
    
# class PredictVQC(APIView):

#     def post(self,request):
#         vqc = VQC(request.data["feature_map"], request.data["ansatz"])
#         v = vqc.load(request.data.get("model_name"))
#         return JsonResponse(output, safe = False)