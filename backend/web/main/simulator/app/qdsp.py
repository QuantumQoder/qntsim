import time
from math import inf
from typing import Any, Dict

import numpy as np
from qntsim.communication.error_analyzer import ErrorAnalyzer
from qntsim.communication.network import Network
from qntsim.communication.utils import to_binary, to_characters
from qntsim.components.photon import Photon
from qntsim.components.waveplates import HalfWaveplate
from qntsim.kernel.event import Event
from qntsim.kernel.timeline import Timeline
from qntsim.topology.node import EndNode
from qntsim.topology.topology import Topology
from qntsim.utils.encoding import polarization
from qntsim.utils.log import logger


def qdsp(topology:Dict, app_settings:Dict[str, Dict[str, Any]]):
    response = {}
    message1 = app_settings.get("sender").get("message")
    message2 = app_settings.get("receiver").get("message")
    _is_binary, messages = to_binary(messages=[message1, message2])

    
    start_time = time.time()
    simulator = Timeline(stop_time=app_settings.get("stoptime", inf), backend=app_settings.get("backend", "Qutip"))
    configuration = Topology(name="qdsp", timeline=simulator)
    configuration.load_config_json(config=topology)
    logger.debug("loaded topology into the simulator")
    src_node:EndNode = configuration.nodes.get(app_settings.get("sender").get("node"))
    dst_node:EndNode = configuration.nodes.get(app_settings.get("receiver").get("node"))
    initial_states = np.random.randint(4, size=len(messages[0]))
    basis = polarization.get("bases")
    _quantum_state = {0:basis[0][0],
                      1:basis[0][1],
                      2:basis[1][0],
                      3:basis[1][1]}

    simulator.is_running = True
    logger.info("|------------------Simulation started------------------|")
    photons = [Photon(name=state, quantum_state=_quantum_state[state]) for state in initial_states]
    logger.info("Photons generated for the transmission")
    logger.info("|---------------Encoding process started---------------|")
    hwp = HalfWaveplate(name=np.pi/2, timeline=simulator)
    for photon, msg in zip(photons, messages[0]):
        simulator.events.push(event=Event(time=simulator.now()+time.time(), owner=src_node, activation_method="send_qubit", act_params=[dst_node.name, hwp.apply(qubit=photon) if int(msg) else photon]))
        logger.debug(f"Generated event for sending qubit to {dst_node.name} node")
    simulator.init()
    simulator.run()
    photons = dst_node.qubit_buffer.get(1, [])
    print("final photons,", photons)
    logger.info(f"Photons received at {dst_node.name} node")

    logger.info("|--------------Masurement and Decoding started------------|")
    results = [Photon.measure(basis=basis[photon.name//2], photon=hwp.apply(qubit=photon) if int(msg) else photon) for photon, msg in zip(photons, messages[1])]
    strings = ["".join([str(result^int(char)^(state%2)) for result, char, state in zip(results, message, initial_states)]) for message in messages]
    print(initial_states)
    print(messages)
    print(results)
    print(strings)
    simulator.is_running = False
    logger.info(f"|-------------Simulation Completed!! Message has been safely transferred from {src_node.name} to {dst_node.name}----------------------|")

    
    recv_msgs = to_characters(bin_strs=strings, _was_binary=_is_binary)
    end_time = time.time()
    network = Network(topology=topology,
                      messages={(app_settings.get("sender").get("node"),
                                 app_settings.get("receiver").get("node")):messages[0],
                                (app_settings.get("receiver").get("node"),
                                 app_settings.get("sender").get("node")):messages[1]},
                      require_entanglement=False)
    network._strings = strings
    _, _, err_prct, err_sd, info_lk, msg_fidelity = ErrorAnalyzer._analyse(network=network)
    app_settings.update(output_msg=recv_msgs, avg_err=err_prct, std_dev=err_sd, info_leak=info_lk, msg_fidelity=msg_fidelity)
    response["application"] = app_settings
    print("response", response)
    from main.simulator.topology_funcs import network_graph
    response = network_graph(network_topo=configuration, source_node_list=[src_node.name], report=response)
    response["performance"]["execution_time"] = end_time - start_time

    return response


if __name__=="__main__":
    topology = {
        'nodes': [
            {
                'name': 'node1',
                'type': 'end',
                'memo_size': 500,
                'memory': {
                    'frequency': 80000000,
                    'expiry': -1,
                    'efficiency': 1,
                    'fidelity': 0.93
                    },
                'lightSource': {
                    'frequency': 80000000,
                    'wavelength': 1550,
                    'bandwidth': 0,
                    'mean_photon_num': 0.1,
                    'phase_error': 0
                    }
                },
            {
                'name': 'node2',
                'type': 'end',
                'memo_size': 500,
                'memory': {
                    'frequency': 80000000,
                    'expiry': -1,
                    'efficiency': 1,
                    'fidelity': 0.93
                    },
                'lightSource': {
                    'frequency': 80000000,
                    'wavelength': 1550,
                    'bandwidth': 0,
                    'mean_photon_num': 0.1,
                    'phase_error': 0
                    }
                }
            ],
        'quantum_connections': [
            {
                'nodes': ['node1', 'node2'],
                'attenuation': 0.1,
                'distance': 70
                }
            ],
        'classical_connections': [
            {
                'nodes': ['node1', 'node1'],
                'delay': 0,
                'distance': 0
                },
            {
                'nodes': ['node1', 'node2'],
                'delay': 10000000000,
                'distance': 1000
                },
            {
                'nodes': ['node2', 'node1'],
                'delay': 10000000000,
                'distance': 1000
                },
            {
                'nodes': ['node2', 'node2'],
                'delay': 0,
                'distance': 0
                }
            ],
        'detector': {
            'efficiency': 1,
            'count_rate': 25000000,
            'time_resolution': 150
            }
        }
    app_settings = \
        {
            "sender":
                {
                    "node":"node1",
                    "message":"h",
                },
            "receiver":
                {
                    "node":"node2",
                    "message":"m",
                },
            "backend":"Qutip",
            "stoptime":1e12
        }
    print("response", qdsp(topology=topology, app_settings=app_settings))