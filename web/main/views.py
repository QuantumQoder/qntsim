import time
import json
import io
import networkx as nx
import matplotlib.pyplot as plt
import base64
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.template import loader
from main.simulator.topology_funcs import *
from django.views.decorators.http import condition
from django.views.decorators.csrf import csrf_exempt

def index(request):
	context = {
		"title": "QNT Simulator"
	}
	return render(request, 'app.html', context)

def fetchAppOptions(request):
	app = request.GET.get('app')
	context = {
		"nodes": json.loads(request.GET.get('nodes')),
	}
	# print(type(context))
	return render(request, f'appOpts/{app}.html', context)

@csrf_exempt
def graph(request):
    # for key, value in request.POST.items():
    #     print('Key: %s' % (key) ) 
    #     # print(f'Key: {key}') in Python >= 3.7
    #     print('Value %s' % (value) )
    topology = json.loads(request.POST['topology'])
    print(f"Request received to make topology graph: {str(topology)}")
    if topology is not None:
        buffer = io.BytesIO()
        graph = graph_topology(topology)
        nx.draw(graph, with_labels=True)
        plt.savefig(buffer, dpi=300, bbox_inches='tight', format="png")
        plt.show()
        buffer.seek(0)
        figdata_png = base64.b64encode(buffer.getvalue())
        context = {
			"b64String": figdata_png.decode('utf8'),
		}
        return render(request, f'topologyGraph.html', context)

@condition(etag_func=None)
def appLog(request):
	print("Fetching App Logs")
	
	resp = HttpResponse( stream_response_generator(), content_type='text/html')
	return resp

def stream_response_generator():
    yield ""
    for x in range(1,100):
        yield "%s\n" % x
        yield " " * 1024  # Encourage browser to render incrementally
        time.sleep(0.5)

def example(request):

	# topFile = 'topology/simulator/' + request.GET['topology']
	# topoObj = tlexample(topFile, request.GET['node1'], request.GET['node2'])
	# columns = [{'field': f, 'title': f} for f in MEMORY_COLS]
	memoryData = tlexample('main/simulator/4node.json', 'a', 'b')
	print(memoryData)
	context = {
		"data": memoryData,
		# "columns": columns
	}
	return render(request, 'example.html', context)