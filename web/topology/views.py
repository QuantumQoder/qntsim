from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.template import loader
from topology.simulator.topology_funcs import *

def index(request):
	context = {
		"title": "Load Topology"
	}
	return render(request, 'load_topology.html', context)

def graph(request):
	topDir = r'D:\Qulabz-Code\QNTSIM\front\QNTSIM\topology\simulator'
	topFile = topDir + '\\' + request.GET['topology']
	topoObj = graph_topology(topFile)
	if topoObj:
		return JsonResponse({'success':'true'})
	else:
		return JsonResponse({'success':'false'}) 