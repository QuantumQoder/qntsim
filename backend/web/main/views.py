from re import S
import time
import json
import base64
import io
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from main.simulator.topology_funcs import *
from django.views.decorators.http import condition
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework import mixins, generics
from main.serializers import ApplicationSerializer
from main.models import Applications,Results


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


    def post(self,request):
        

        print('request', request.data.get('topology'))
        topology = request.data.get('topology')
        application_id = request.data.get('application')
        appSettings = request.data.get('appSettings')
        # Add check for getting application id and extracting name.
        print('application id', application_id)
        application = Applications.objects.filter(id = application_id).values("name").first().get('name')
        print(f"Running applications: {application}", appSettings)
        print('request user', request.user.username, request.user.id)
        results = {}

        if application == "e91":
            results = e91(topology, appSettings["sender"], appSettings["receiver"], int(appSettings["keyLength"]))
        elif application == "e2e":
            print('e2e',appSettings["sender"], appSettings["receiver"], appSettings["startTime"], appSettings["size"], appSettings["priority"], appSettings["targetFidelity"], appSettings["timeout"])
            results = e2e(topology, appSettings["sender"], appSettings["receiver"], appSettings["startTime"], appSettings["size"], appSettings["priority"], appSettings["targetFidelity"], appSettings["timeout"] )
        elif application == "ghz":
            results = ghz(topology, appSettings["endnode1"], appSettings["endnode2"], appSettings["endnode3"], appSettings["middlenode"] )
        elif application == "ip1":
            results = ip1(topology, appSettings["sender"], appSettings["receiver"], appSettings["message"] )
        elif application == "ping_pong":
            results = ping_pong(topology, appSettings["sender"], appSettings["receiver"], int(appSettings["sequenceLength"]), appSettings["message"] )
        elif application == "qsdc1":
            results = qsdc1(topology, appSettings["sender"], appSettings["receiver"], int(appSettings["sequenceLength"]), appSettings["key"] )
        elif application == "teleportation":
            results = teleportation(topology, appSettings["sender"], appSettings["receiver"], complex(appSettings["amplitude1"]), complex(appSettings["amplitude2"]) )
        elif application == "qsdc_teleportation":
            results = qsdc_teleportation(topology, appSettings["sender"], appSettings["receiver"], appSettings["message"], appSettings["attack"])
        elif application == "single_photon_qd":
            print('inside')
            results = single_photon_qd(topology, appSettings["sender"], appSettings["receiver"], appSettings["message1"],appSettings["message2"], appSettings["attack"])
        elif application == "mdi_qsdc":
            results = mdi_qsdc(topology, appSettings["sender"], appSettings["receiver"], appSettings["message"], appSettings["attack"])
        elif application == "ip2":
            input_messages = {int(k):str(v) for k,v in appSettings["input_messages"].items()}
            ids = {int(k):str(v) for k,v in appSettings["ids"].items()}
            results = ip2(topology,input_messages,ids,appSettings["num_check_bits"],appSettings["num_decoy"])
        # Add code for results here
        # print('results', results)
        # graphs = results.get('graph')
        # output = results.get('results')
        output = results
        # print('graphs', graphs)
        # print('output', output)
        # print('request user', request.user)
        # res = Results.objects.create(user = request.user, topology = topology, app_name = application, input =appSettings, output = output,graphs = graphs)
        # res.save()

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


