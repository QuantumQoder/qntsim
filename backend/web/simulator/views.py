from unittest import result
from django.shortcuts import render

from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
import json
from simulator.models import Results
from rest_framework import mixins, generics
from main.simulator.topology_funcs import *
from simulator.serializers import ApplicationSerializer
from simulator.models import Applications

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

        # Add code for results here
        print('results', results)
        graphs = results.get('graph')
        # output = results.get('results')
        output = results
        print('graphs', graphs)
        print('output', output)
        res = Results.objects.create(user = request.user, topology = topology, app_name = application, input =appSettings, output = output,graphs = graphs)
        res.save()

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