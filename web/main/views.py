import time
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.template import loader
from main.simulator.topology_funcs import *
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import condition

def index(request):
	context = {
		"title": "QNT Simulator"
	}
	return render(request, 'app.html', context)

def makeGraph(request):

	topFile = 'main/simulator/' + request.GET['topology']
	topoObj = graph_topology(topFile)

	if topoObj:
		return JsonResponse({'success':'true'}) 
	else:
		return JsonResponse({'success':'false'}) 

@xframe_options_exempt
def graph(request):
	topology = request.GET.get('topology')
	if topology is not None:
		topFile = 'main/simulator/' + request.GET['topology']
		topoObj = graph_topology(topFile)
	
	context = {
		"title": "Topology Graph"
	}
	return render(request, 'graph.html', context)

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