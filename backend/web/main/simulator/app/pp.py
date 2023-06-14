import time
from functools import partial
from typing import Any, Dict

from numpy.random import choice, randint
from qntsim.communication import (Network, ProtocolPipeline,
                                  bell_type_state_analyzer)
from qntsim.components.circuit import QutipCircuit
from qntsim.topology.node import EndNode


def ping_pong(topology:Dict, app_settings:Dict):
    s = time.time()
    print(s)
    try:
        response = {}
        start_time = time.time()
        protocol = ProtocolPipeline(
            messages_list=[
                {
                    (
                        app_settings.get("sender").get("node"),
                        app_settings.get("receiver").get("node")
                    ):app_settings.get("sender").get("message")
                }],
            encode=partial(encode, mode_switch_prob=app_settings.get("sender").get("switchProb", 0.25)))
        received_msgs, avg_err, std_dev, info_leak, msg_fidelity = protocol(topology=topology, size=lambda x:x//(1-app_settings.get("sender").get("switchProb", 0.25)), require_entanglement=True)
        end_time = time.time()
        app_settings.update(output_msg=received_msgs, avg_err=avg_err, std_dev=std_dev, info_leak=info_leak, msg_fidelity=msg_fidelity)
        response["application"] = app_settings
        from main.simulator.topology_funcs import network_graph
        response = network_graph(network_topo=protocol.networks[0]._net_topo, source_node_list=[app_settings.get("sender").get("node")], report=response)
        response["performance"]["execution_time"] = end_time - start_time
    except Exception:
        raise
    finally:
        e = time.time()
        print(divmod(e-s, 60))

    return response

def encode(network:Network, _, msg_index:int, mode_switch_prob:float):
    print(network)
    src_node:EndNode = network.nodes[msg_index]
    message = network._bin_msgs[msg_index]
    msg_iter = iter(message)
    ctrl_meas_basis = []
    something = {}
    for info in src_node.resource_manager.memory_manager:
        print("info", info.state)
        if info.state != "ENTANGLED": break
        qtc = QutipCircuit(1)
        qtc = network._add_noise(err_type="reset", qtc=qtc)
        with choice(a=["service", "control"], p=[1-mode_switch_prob, mode_switch_prob]) as mode:
            match mode:
                case "message":
                    if int(next(msg_iter)):
                        qtc.x(0)
                    if int(next(msg_iter)):
                        qtc.z(0)
                case "control":
                    ctrl_meas_basis.append(randint(2))
                    if ctrl_meas_basis[-1]: qtc.h(0)
                    qtc.measure(0)
        key = info.memory.qstate_key
        state = network.manager.get(key)
        something[tuple(sorted(state.keys))] = network.manager.run_circuit(circuit=qtc, keys=[key]).get(key)

    print("something", something)

    return something, ctrl_meas_basis

def decode(network:Network, returns:Any):
    something, ctrl_meas_basis = returns[0], returns[1]
    bsa = bell_type_state_analyzer(2)
    for keys, result in something.items():
        if result:
            qtc = QutipCircuit(1)
            qtc = network._add_noise(err_type="reset", qtc=qtc)
            qtc.measure(0)
            output = network._add_noise(err_type="readout", qtc=qtc, keys=keys[-1:])
        else:
            output = network._add_noise(err_type="readout", qtc=bsa, keys=keys)
        print(result, output)

if __name__=="__main__":
    topology = \
        {
        "nodes": [
            {
                "Name": "n1",
                "Type": "end",
                "noOfMemory": 500,
                "memory": {
                    "frequency": 8000000,
                    "expiry": 2000,
                    "efficiency": 0,
                    "fidelity": 0.93
                }
            },
            {
                "Name": "n2",
                "Type": "end",
                "noOfMemory": 500,
                "memory": {
                    "frequency": 8000000,
                    "expiry": 2000,
                    "efficiency": 0,
                    "fidelity": 0.93
                }
            }
        ],
        "quantum_connections": [
            {
                "Nodes": [
                    "n1",
                    "n2"
                ],
                "Attenuation": 0.00001,
                "Distance": 70
            }
        ],
        "classical_connections": [
            {
                "Nodes": [
                    "n1",
                    "n1"
                ],
                "Delay": 0,
                "Distance": 1000
            },
            {
                "Nodes": [
                    "n1",
                    "n2"
                ],
                "Delay": 1000000000,
                "Distance": 1000
            },
            {
                "Nodes": [
                    "n2",
                    "n1"
                ],
                "Delay": 1000000000,
                "Distance": 1000
            },
            {
                "Nodes": [
                    "n2",
                    "n2"
                ],
                "Delay": 0,
                "Distance": 1000
            }
        ]
    }
    app_settings = \
        {
            "sender":
                {
                    "node": "n1",
                    "message": "01",
                    "switchProb": 0.3
                },
            "receiver":
                {
                    "node": "n2",
                }
        }
    print(ping_pong(topology=topology, app_settings=app_settings))