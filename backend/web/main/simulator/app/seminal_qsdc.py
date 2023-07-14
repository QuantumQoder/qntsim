import logging
import time
from statistics import mean
from typing import Dict, Tuple

from numpy.random import choice
from qntsim.communication import Network
from qntsim.components.circuit import QutipCircuit
from qntsim.topology.node import EndNode

logger = logging.getLogger("main.application.seminal_qsdc")

def seminal_qsdc(topology:Dict, app_settings:Dict):
    s = time.time()
    try:
        response = {}
        start_time = time.time()
    except:
        raise
    finally:
        e = time.time()
        print(divmod(e-s, 60))

def encode(network:Network, _):
    pass



def foo1(network:Network, _, node_name:str, err_threshold1:float=0.5):
    measured_pairs = {}
    node:EndNode = network._net_topo.nodes.get(node_name)
    qtc = QutipCircuit(1)
    qtc = network._add_noise(err_type="reset", qtc=qtc)
    qtc.measure(0)
    for info in node.resource_manager.memory_manager:
        if info.state!="ENTANGLED":
            break
        if choice([0, 1], p=[1-err_threshold1, err_threshold1]):
            key = info.memory.qstate_key
            state = network.manager.get(key=key)
            measured_pairs[tuple(state.keys)] = network._add_noise(err_type="readout", qtc=qtc, keys=[key])
            info.to_raw()
    return measured_pairs

def first_check(network:Network, measured_pairs:Dict[Tuple[int], Dict[int, int]]):
    logger.info("First security check initiated")
    qtc = QutipCircuit(1)
    qtc = network._add_noise(err_type="reset", qtc=qtc)
    qtc.measure(0)
    if mean(network._bell_pairs.get(keys) == (network._add_noise(err_type="readout", qtc=qtc, keys=set(keys)-set(output)).get(set(keys)-set(output)), output.get(list(output)[0])) for keys, output in measured_pairs.items())>0.75:
        logger.error("Eavesdropper detected during first check")
        return {"Err_msg":"Eavesdropper detected in first check!!"}
    logger.info("First security check passed")

def second_check(network:Network, err_msg:Dict[str], node_name:str, err_threshold2:float=0.5):
    if err_msg: return err_msg
    logger.info("Second security check initiated")
    node:EndNode = network._net_topo.nodes.get(node_name)
    qtc = QutipCircuit(2)
    qtc = network._add_noise(err_type="reset", qtc=qtc)
    qtc.cx(0, 1)
    qtc.h(0)
    qtc.measure(0)
    qtc.measure(1)
    # for info in node.resource_manager.memory_manager:
        # if info.state != ""
    if mean((bell_pair:=network._bell_pairs.get((keys:=network.manager.get(info.memory.qstate_key)))) == ((output:=network._add_noise(err_type="readout", qtc=qtc, keys=keys)).get(keys[0]), output.get(keys[1])) if choice([0, 1], p=[1-err_threshold2, err_threshold2]) else bell_pair for info in node.resource_manager.memory_manager if info.state=="ENTANGLED")>0.75:
        logger.error("Eavesdropper detected during first check")
        return {"Err_msg":"Eavesdropper detected in first check!!"}
    logger.info("Second security check initiated")


if __name__=="__main__":
    topology = {
        'nodes': [
            {
                'Name': 'node1',
                'Type': 'end',
                'noOfMemory': 500,
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
                'Name': 'node2',
                'Type': 'end',
                'noOfMemory': 500,
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
                'Nodes': ['node1', 'node2'],
                'Attenuation': 0.1,
                'Distance': 70
                }
            ],
        'classical_connections': [
            {
                'Nodes': ['node1', 'node1'],
                'Delay': 0,
                'Distance': 0
                },
            {
                'Nodes': ['node1', 'node2'],
                'Delay': 10000000000,
                'Distance': 1000
                },
            {
                'Nodes': ['node2', 'node1'],
                'Delay': 10000000000,
                'Distance': 1000
                },
            {
                'Nodes': ['node2', 'node2'],
                'Delay': 0,
                'Distance': 0
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
                    "node": "n1",
                    "message": "01",
                    "switchProb": 0.3
                },
            "receiver":
                {
                    "node": "n2"
                }
        }