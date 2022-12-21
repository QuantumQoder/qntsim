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

@csrf_exempt
def run(request):
    
    topology = json.loads(request.POST['topology'])
    application = request.POST['application']
    appSettings = json.loads(request.POST['appSettings'])
    
    # print(f"Running applications: {application}")
    # print("hhhh")
    results = {}

    if application == "e91":
        results = e91(topology, appSettings["sender"], appSettings["receiver"], int(appSettings["keyLength"]))
    elif application == "e2e":
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
        results = qsdc_teleportation(topology, appSettings["sender"], appSettings["receiver"], appSettings["message"])
    elif application == "single_photon_qd":
        print('inside')
        results = single_photon_qd(topology, appSettings["sender"], appSettings["receiver"], appSettings["message1"],appSettings["message2"],appSettings["num_photons"])
    print("results = ",results)
    return render(request, f'apps/{application}/results.html', results)

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


