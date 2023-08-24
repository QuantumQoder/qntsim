# from main.models import Gates, GateTypes, Layers, CircuitModel, LayerGates

# def quantum_circuit_service(self,request):
#         # circuit_id = request.data.get("circuit_id")
#         # layer_id = request.data.get("layer_id")
#         # gate_id =   request.data.get("gate_id")
#         # gate_inputs = request.data.get("gate_inputs")
#         gate_type = GateTypes(
#         gt_name="H",
#         single_multiple="Single",
#         gt_description="Hadamard Gate"
#         )
#         gate_type.save()
#         return {"status":"success"}


# def add_gate_service(self,request):
#     request_data = request.data
#     print(request_data)
#     gate_type = GateTypes(
#         gt_name=request.data.get("gt_name"),
#         single_multiple=request.data.get("single_multiple"),
#         gt_description=request.data.get("gt_description")
#     )

#     gate_type.save()

#     return {"status":"success"}

# def getCircuits():
#         circuits = CircuitModel.objects.all()
#         circuit_list=[]
#         for circuit in circuits:
#                 list ={}
#                 list["id"] = circuit.circuit_id
#                 list["name"] = circuit.name
#                 list["description"] = circuit.description
#                 circuit_list.append(list)
#         return circuit_list

