from qntsim.communication.interface import Interface

import os

for filename in os.listdir():
    print(filename)
print(__file__)

topology = {"nodes":[{"Name":"n1",
                      "Type":"end",
                      "noOfMemory":500},
                     {"Name":"n2",
                      "Type":"end",
                      "noOfMemory":500}],
            "quantum_connections":[{"Nodes":["n1", "n2"],
                                    "Attenuation":1e-5,
                                    "Distance":600}],
            "classical_connections":[{"Nodes":["n1", "n2"],
                                      "Delay":1e-5,
                                      "Distance":600}]}

messages = {("n1", "n2"):"h"}

print(topology, messages)
print(Interface)

interface = Interface(topology=topology, messages=messages, stop_time=10e12, end_time=5e12, timeout=1e12)

print(interface)
# print(interface.events)
print(repr(interface))