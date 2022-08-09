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
