from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.template import loader
from topology.simulator.topology_funcs import *

def index(request):
	context = {
		"title": "Load Topology"
	}
	return render(request, 'load_topology.html', context)

def makeGraph(request):

	topFile = 'topology/simulator/' + request.GET['topology']
	topoObj = graph_topology(topFile)

	if topoObj:
		return JsonResponse({'success':'true'}) 
	else:
		return JsonResponse({'success':'false'}) 


def graph(request):
	context = {
		"title": "Topology Graph"
	}
	return render(request, 'graph.html', context)

def example(request):

	# topFile = 'topology/simulator/' + request.GET['topology']
	# topoObj = tlexample(topFile, request.GET['node1'], request.GET['node2'])
	# columns = [{'field': f, 'title': f} for f in MEMORY_COLS]
	memoryData = tlexample('topology/simulator/4node.json', 'a', 'b')
	print(memoryData)
	context = {
		"data": memoryData,
		# "columns": columns
	}
	return render(request, 'example.html', context)