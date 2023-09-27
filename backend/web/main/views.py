import base64
import io
import json
import time
from re import S

import matplotlib
import networkx as nx

matplotlib.use('Agg')
import importlib
import logging
import os
import time

import matplotlib.pyplot as plt
import qntsim
import websocket
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import condition
# from main.models import Applications, Results, Gates
from main.models import Applications, Results
from main.serializers import ApplicationSerializer
from main.simulator.app.ip2 import ip2_run
from main.simulator.app.qdsp import qdsp
from main.simulator.topology_funcs import *
from qntsim.utils import log
from rest_framework import generics, mixins, permissions
from rest_framework.views import APIView
# from models import 
# from .services.quantumcircuit_service import getCircuits, quantum_circuit_service, add_gate_service
def home(request):
    context = {
        "title": "QNT Simulator"
    }
    return render(request, 'home.html', context)

def apps(request):
    app = request.GET.get('app')
    if app:
        context = {
            "title": app,
            "app": app
        }
        return render(request, f'apps/{app}/index.html', context)
    else:
        context = {
            "title": "QNT Simulator"
        }
        
        return render(request, 'apps.html', context)

def fetchAppOptions(request):
    app = request.GET.get('app')
    context = {
        "nodes": json.loads(request.GET.get('nodes')),
    }
    # print(type(context))
    return render(request, f'apps/{app}/config.html', context)




class RunApp(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)  # Allow any user to access

    def post(self,request):
        ############### configuring logger ###############
        log.set_logger("m")
        log.set_logger_level('DEBUG')
        print("handlers:", log.logger.handlers)
        topology = request.data.get('topology')
        application_id = request.data.get('application')
        appSettings = request.data.get('appSettings')
        debug = request.data.get('debug')
        
        
        modules  = {'physical': ['interferometer',
                    'spdc_lens',
                    'beam_splitter',
                    'DLCZ_bsm',
                    'light_source',
                    'circuit',
                    'bk_memory',
                    'polarization_measurement',
                    'bk_bsm',
                    'switch',
                    'optical_channel',
                    'waveplates',
                    'photon',
                    'detector',
                    'DLCZ_memory'],
                    'link': ['bk_purification',
                    'DLCZ_generation',
                    'DLCZ_purification',
                    'entanglement_protocol',
                    'bk_swapping',
                    'DLCZ_swapping',
                    'bk_generation'],
                    'network': ['node'],
                    'transport': ['transport_manager'],
                    'application': ['ip1_',
                    'pp',
                    'ghz',
                    'qsdc_teleportation',
                    'mdi_qsdc',
                    'single_photon_qd',
                    'ping_pong',
                    'teleportation',
                    'e91',
                    'utils',
                    'e2e',
                    'qss',
                    'ip1',
                    'qsdc1',
                    'qdsp',
                    'ip2'],
                    "eventSimulation":['timeline']}
        
        selected_modules = debug["modules"]#["transport"]
        print("selected_modules:", selected_modules)
        for module in selected_modules:
            for file in modules[module]:
                log.track_module(file)
        
        
        importlib.reload(qntsim)
        topology = request.data.get('topology')
        application_id = request.data.get('application')
        appSettings = request.data.get('appSettings')
        application = Applications.objects.filter(id = application_id).values("name").first().get('name')
        debug = request.data.get('debug')
        results = {}

        if application == "e91":
            #print("e91 views")
            results = e91(topology, appSettings["sender"], appSettings["receiver"], int(appSettings["keyLength"]))
        elif application == "e2e":
            print('e2e',appSettings["sender"], appSettings["receiver"], appSettings["startTime"], appSettings["size"], appSettings["priority"], appSettings["targetFidelity"], appSettings["timeout"])
            results = e2e(topology, appSettings["sender"], appSettings["receiver"], appSettings["startTime"], appSettings["size"], appSettings["priority"], appSettings["targetFidelity"], appSettings["timeout"] )
        elif application == "ghz":
            results = ghz(topology, appSettings["endnode1"], appSettings["endnode2"], appSettings["endnode3"], appSettings["middlenode"] )
        elif application == "ip1":
            results = ip1(topology, appSettings["sender"]["node"], appSettings["receiver"]["node"], appSettings["sender"]["message"] )
        elif application == "ping_pong":
            results = ping_pong(topology=topology, app_settings=appSettings)
        elif application == "qsdc1":
            results = qsdc1(topology, appSettings["sender"], appSettings["receiver"], int(appSettings["sequenceLength"]), appSettings["key"] )
        elif application == "teleportation":
            results = teleportation(topology, appSettings["sender"], appSettings["receiver"], complex(appSettings["amplitude1"]), complex(appSettings["amplitude2"]) )
        elif application == "qsdc_teleportation":
            results = qsdc_teleportation(topology, appSettings["sender"]["node"], appSettings["receiver"]["node"], appSettings["sender"]["message"], appSettings["attack"])
        elif application == "single_photon_qd":
            results = qdsp(topology=topology, app_settings=appSettings)
            # results = single_photon_qd(topology, appSettings["sender"], appSettings["receiver"], appSettings["message1"],appSettings["message2"], appSettings["attack"])
        elif application == "mdi_qsdc":
            results = mdi_qsdc(topology, appSettings["sender"], appSettings["receiver"], appSettings["message"], appSettings["attack"])
        elif application == "ip2":
            results = ip2_run(topology,appSettings)
            
        output = results
        print(debug["logLevel"])
        debug_levels = {"debug": "DEBUG", "info":"INFO"}
        print(debug_levels[debug["logLevel"]])
        log_level = debug_levels[debug["logLevel"]]
        logs = log.read_from_memory(log.logger, level = log_level)
        output["logs"] = logs
        
        
        return JsonResponse(output, safe = False)



class ApplicationList(mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    generics.GenericAPIView,
    mixins.UpdateModelMixin):

    queryset =Applications.objects.all()
    serializer_class = ApplicationSerializer
    lookup_field = 'pk'
    # authentication_classes = [authentication.SessionAuthentication]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk is not None:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        # queryset = PortfolioDetails.objects.get(id = request.data.get("portfolio_id"))
        return self.partial_update(request, *args, **kwargs)



class PastResultsList(generics.GenericAPIView):

    def get(self, request):

        results = Results.objects.filter(user = request.user)
        print('all results', results)
        result_list=[]
        for result in results:
            list ={}
            list["id"] = result.id
            list["name"] = result.app_name
            list["time"] = result.created_at
            list["descryption"] = "Completed" 
            result_list.append(list)
        print('result', result_list,result.user, result.created_at)
        return JsonResponse(result_list, safe =False)



class ApplicationResult(generics.GenericAPIView):


    def get(self, request):
        result_id = request.data.get('id')
        result = Results.objects.filter(id = result_id).values().first()
        print('result', result)
        return JsonResponse(result)

# class QuantumCircuitExecuter(generics.GenericAPIView):

#     def post(self, request):
#         status = quantum_circuit_service(self,request)
#         return JsonResponse(status)
    

class AddGate(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)  # Allow any user to access

    def get(self,request):
        try:
            gates = Gates.objects.all()
            print(gates)
            gate_list=[]
            for gate in gates:
                list ={ }
                list["id"] = gate.gate_id
                # list["gt_id"] = gate.gt_id.gt_id
                # list["gt_name"] = gate.gt_id.gt_name
                # list["single_multiple"] = gate.gt_id.single_multiple
                # list["gt_description"] = gate.gt_id.gt_description
                list["gate_name"] = gate.gate_name
                list["gate_description"] = gate.gate_description
                gate_list.append(list)
            return JsonResponse(gate_list, safe =False)
        except Exception as e:
            return JsonResponse({"status":"failed","error":str(e)},status = 500)

    def post(self, request):
        try:
                request_data = request.data

                for gate in request_data:
                    # print(gate)
                    gate = Gates(
                        gate_name=gate.get("gate_name"),
                        gate_description=gate.get("gate_description")
                    )
                    gate.save()
                return JsonResponse({"status":"success"})
        except Exception as e:
                return JsonResponse({"status":"failed","error":str(e)},status = 500) 
        
    def put(self,request):
        try:
            gate = Gates.objects.get(gate_id=request.data.get("gate_id"))
            gate.gate_name = request.data.get("gate_name")
            gate.gate_description = request.data.get("gate_description")
            gate.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status":"failed","error":str(e)},status = 500)
        
    def delete(self,request):
        try:
            gate = Gates.objects.all()
            gate.delete()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status":"failed","error":str(e)},status = 500)    
        
class BaseCircuit(generics.GenericAPIView):

    def post(self, request):
        try:
            print(request)
            print(request.data)
            # custom_executor(**request.data)

            return JsonResponse({"status":"success"})
        except Exception as e:
            return JsonResponse({"status":"failed","error":str(e)})   

@csrf_exempt
def testrun(request):
    
    topology = json.loads(request.POST['topology'])
    application = request.POST['application']
    appSettings = json.loads(request.POST['appSettings'])
    
    print(f"Running applications: {application}")
    
    results = {}

    if application == "e91":
        results = e91(topology, appSettings["sender"], appSettings["receiver"], int(appSettings["keyLength"]))
    elif application == "e2e":
        results = e2e(topology, appSettings["sender"], appSettings["receiver"], appSettings["startTime"], appSettings["size"], appSettings["priority"], appSettings["targetFidelity"], appSettings["timeout"] )
        return render(request, f'apps/{application}/results.html', results)
        ##TODO: Json format
    elif application == "ghz":
        res = ghz(topology, appSettings["endnode1"], appSettings["endnode2"], appSettings["endnode3"], appSettings["middlenode"] )
        results={
            "alice_state":str(res["alice_state"].tolist()),
            "bob_state":str(res["bob_state"].tolist()),
            "charlie_state":str(res["charlie_state"].tolist()),
            "middle_state":str(res["ghz_state"].tolist())
        }
    elif application == "ip1":
        results = ip1(topology, appSettings["sender"], appSettings["receiver"], appSettings["message"] )
    elif application == "ping_pong":
        results = ping_pong(topology, appSettings["sender"], appSettings["receiver"], int(appSettings["sequenceLength"]), appSettings["message"] )
    elif application == "qsdc1":
        results = qsdc1(topology, appSettings["sender"], appSettings["receiver"], int(appSettings["sequenceLength"]), appSettings["key"] )
    elif application == "teleportation":
        res = teleportation(topology, appSettings["sender"], appSettings["receiver"], complex(appSettings["amplitude1"]), complex(appSettings["amplitude2"]) )
        results = {
            "alice_bob_entanglement": str(res["alice_bob_entanglement"]),
            "random_qubit" : str(res["random_qubit"]),
            "meas_rq":res["meas_rq"],
            "meas_r1":res["meas_r1"],
            "bob_initial_state" : str(res["bob_initial_state"]),
            "bob_final_state" : str(res["bob_final_state"])
        }

    print(results)
    return JsonResponse(results)

@csrf_exempt
def graph(request):
    topology = json.loads(request.POST['topology'])
    print(f"Request received to make topology graph: {str(topology)}")
    if topology is not None:
        buffer = io.BytesIO()
        graph = graph_topology(topology)
        print(graph)
        nx.draw(graph, with_labels=True)
        plt.savefig(buffer, dpi=300, bbox_inches='tight', format="png")
        buffer.seek(0)
        figdata_png = base64.b64encode(buffer.getvalue())
        buffer.truncate(0)
        context = {
            "b64String": figdata_png.decode('utf8'),
        }
        plt.clf()
        return render(request, f'topologyGraph.html', context)


@condition(etag_func=None)
def appLog(request):
    print("Fetching App Logs")

    resp = HttpResponse(stream_response_generator(), content_type='text/html')
    return resp


def stream_response_generator():
    yield ""
    for x in range(1, 100):
        yield "%s\n" % x
        yield " " * 1024  # Encourage browser to render incrementally
        time.sleep(0.5)

@csrf_exempt
def stream_logs(request):
    def generate_response():
        print('pwd',os.getcwd())
        with open('/code/web/qsdc_tel.log', 'r') as f:
            while True:
                line = f.readline()
                print('line', line)
                if not line:
                    time.sleep(1)  # wait for new lines to be added
                else:
                    yield line.encode()

    response = StreamingHttpResponse(generate_response(), content_type='text/plain')
    return response
# @csrf_exempt
# def log_view(request):
    
#     # def stream_logs():
#     memory_handler.websocket = websocket.WebSocket()
#     memory_handler.websocket.connect("http://0.0.0.0:8000/logs")
#     records = memory_handler.buffer
#     for record in records:
#         log = memory_handler.format(record)
#         memory_handler.websocket.send(json.dumps(log))
#     # for handler in logger.handlers:
#     #     logger.removeHandler(handler)
#     print("Logs ended..")
#     #return StreamingHttpResponse(stream_logs(), content_type='text/plain')

# @csrf_exempt
# def log_view(request):
#     def stream_logs():
#         # retrieve log records from the MemoryHandler buffer
#         records = memory_handler.buffer
#         for record in records:
#             # format the log record as a string
#             if record.levelname == "INFO":
#                 log_message = f"{record.levelname}: {record.getMessage()}\n"
#                 # yield the log message to the response stream
#                 yield log_message.encode('utf-8')
    
#     # create a StreamingHttpResponse that streams the log messages
#     response = StreamingHttpResponse(stream_logs(), content_type='text/plain')
#     # set the response status code to 200 OK
#     response.status_code = 200
#     # # set the Content-Disposition header to force download of the log file
#     # response['Content-Disposition'] = 'attachment; filename="my_log_file.txt"'
#     # for handler in logger.handlers:
#     #     logger.removeHandler(handler)
#     # for handler in logger.handlers:
#     #     logger.removeHandler(handler)
#     return response