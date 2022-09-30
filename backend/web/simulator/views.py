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

        topology = json.loads(request.POST['topology'])
        application = request.POST['application']
        appSettings = json.loads(request.POST['appSettings'])
        
        print(f"Running applications: {application}")
        
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

        
        res = Results.objects.create(topology = topology, app_name = application, input =appSettings)
        res.save()

        return JsonResponse(results)



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