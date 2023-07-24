import time
from math import inf
from statistics import mean
from typing import Any, Callable, Dict, Sequence

import numpy as np
from qntsim.communication import (ErrorAnalyzer, Network, __insert_seq__,
                                  __separate_seq__, insert_check_bits,
                                  to_binary, to_string)
from qntsim.components.photon import Photon
from qntsim.components.waveplates import Waveplate
from qntsim.kernel._event import Event
from qntsim.kernel.timeline import Timeline
from qntsim.topology.node import EndNode
from qntsim.topology.topology import Topology
from qntsim.utils.encoding import polarization
from qntsim.utils.log import logger


def ip1(topology:Dict, app_settings:Dict[str, Dict[str, Any]]):
    response = {}
    basis = polarization.get("bases")
    theta = np.random.randint(0, 360)
    message = app_settings.get("sender").get("message")
    _is_binary, messages = to_binary(messages=[message])

    
    start_time = time.time()
    simulator = Timeline( stop_time=app_settings.get("stop_time", inf), backend=app_settings.get("backend", "Qutip"))
    configuration = Topology(name="ip1", timeline=simulator)
    configuration.load_config_json(config=topology)
    logger.debug("loaded topology into the simulator")
    src_node:EndNode = configuration.nodes.get(app_settings.get("sender").get("node"))
    dst_node:EndNode = configuration.nodes.get(app_settings.get("receiver").get("node"))

    simulator.is_running = True
    logger.info("|------------------Simulation started------------------|")
    mod_msg = insert_check_bits(messages=messages, num_check_bits=(num_check_bits:=app_settings.get("sender").get("num_check_bits")))
    logger.debug(f"{num_check_bits} check bits inserted into the message")
    
    logger.info("|---------------Encoding process started---------------|")
    photons = [Photon(name=[theta, char], quantum_state=basis[0][int(char)]) for _, message in mod_msg.items() for char in message]
    logger.info("Message encoded into the photons")
    logger.debug("Message photons generated")
    wp = Waveplate(name=theta, timeline=simulator, angle=theta)
    photons = [wp.apply(qubit=photon) for photon in photons]
    logger.debug(f"Applied {theta}\degree rotation to the message photons")
    sender_id = app_settings.get("sender").get("userID")
    ida_photons = [Photon(name=basis[int(i0)][int(i1)], quantum_state=basis[int(i0)][int(i1)]) for i0, i1 in zip(sender_id[::2], sender_id[1::2])]
    logger.info(f"Sender ID {sender_id} encoded into the photons")
    receiver_id = app_settings.get("receiver").get("userID")
    r = np.random.randint(low=0, high=2, size=len(receiver_id))
    idb_photons = [Photon(name=basis[int(i0)], quantum_state=basis[int(i0)][int(i0)^int(i1)]) for i0, i1 in zip(receiver_id, r)]
    logger.info(f"Receiver ID {receiver_id} encoded into the photons")
    theta_photons = [Photon(name=basis[int(i0)][int(i0)^int(i1)], quantum_state=basis[int(i0)][int(i0)^int(i1)]) for i0, i1 in zip(receiver_id, bin(theta)[2:])]
    decoy_states = np.random.randint(4, size=app_settings.get("sender").get("num_decoy_photons"))
    decoy_photons = [Photon(name=basis[state//2], quantum_state=basis[state//2][state%2]) for state in decoy_states]
    logger.info(f"{len(decoy_states)} decoy photons generated")
    logger.debug("Constructing photon sequence")
    ida_locs, q2 = __insert_seq__(photons, ida_photons)
    idb_locs, q3 = __insert_seq__(q2, idb_photons)
    theta_locs, q4 = __insert_seq__(q3, theta_photons)
    decoy_locs, q5 = __insert_seq__(q4, decoy_photons)
    for photon in q5:
        simulator.events.push(event=Event(time=simulator.now()+time.time(), owner=src_node, activation_method="send_qubit", act_params=[dst_node.name, photon]))
        logger.debug(f"Generated event for sending qubit to {dst_node.name} node")
    simulator.init()
    simulator.run()
    photons_received = dst_node.qubit_buffer.get(1, [])
    logger.info(f"Photons received at {dst_node.name} node")

    logger.info("|--------------Extraction and Decoding started------------|")
    q4_received, received_decoy_meas = extract_seq(indices=decoy_locs, lst=photons_received)
    logger.info("Extracted decoy photons")
    if mean([int(state%2)^int(recv_meas) for state, recv_meas in zip(decoy_states, received_decoy_meas)]) > app_settings.get("err_threshold", 0.25):
        logger.info("Eavesdropper detected in channel")
        return
    q3_received, received_sender_id = extract_seq(indices=ida_locs,
                                                  lst=q4_received,
                                                  list_comp=lambda x: [str(id_bit) for id_pair in [(basis.index(photon.name),
                                                                                                    Photon.measure(basis=photon.name, photon=photon))
                                                                                                   for photon in x]
                                                                       for id_bit in id_pair])
    logger.info("Extracted sender id")
    if mean([int(r_id==s_id) for r_id, s_id in zip(received_sender_id, sender_id)]) > 0.3:
        logger.info("Sender not authenticated")
        return
    q2_received, received_receiver_id = extract_seq(indices=idb_locs, lst=q3_received)
    logger.info("Extracted receiver id")
    if mean([int(r_id==s_id)^r for r_id, s_id, r in zip(received_receiver_id, receiver_id, r)]) > 0.3:
        logger.info("Receiver not authenticated")
        return
    q1_received, received_theta_str = extract_seq(indices=theta_locs, lst=q2_received)
    received_theta = to_string(strings=[received_theta_str], _was_binary=False)
    logger.info("recovered rotation angle from photon sequence received")
    wp = Waveplate(name="-"+received_theta, timeline=simulator, angle=-int(received_theta[0]))
    mod_q1 = "".join([Photon.measure(basis=basis[0], photon=wp.apply(qubit=photon)) for photon in q1_received])
    for positions in mod_msg:
        recv_msg, received_check_bits = __separate_seq__(indices=positions, lst=mod_q1)
        if (msg_integrity := mean([int(mod_q1[index]==chk_bit) for index, chk_bit in zip(positions, received_check_bits)])) > 0.3:
            logger.info(f"Integrity of the message is compromised: {msg_integrity}%")
            return
        break
    simulator.is_running = False
    logger.info(f"|-------------Simulation Completed!! Message has been safely transferred from {src_node.name} to {dst_node.name}----------------------|")

    
    recv_msgs = to_string(strings=[recv_msg], _was_binary=_is_binary)
    end_time = time.time()
    network = Network(topology=topology,
                      messages={(app_settings.get("sender").get("node"),
                                 app_settings.get("receiver").get("node")):app_settings.get("sender").get("message")},
                      require_entanglement=False)
    network._strings = [recv_msg]
    _, _, err_prct, err_sd, info_lk, msg_fidelity = ErrorAnalyzer._analyse(network=network)
    app_settings.update(output_msg=recv_msgs, avg_err=err_prct, std_dev=err_sd, info_leak=info_lk, msg_fidelity=msg_fidelity)
    response["application"] = app_settings
    print("response, ", response)
    from main.simulator.topology_funcs import network_graph
    response = network_graph(network_topo=configuration, source_node_list=[src_node.name], report=response)
    response["performance"]["execution_time"] = end_time - start_time

    return response

def extract_seq(indices:Sequence[int], lst:Sequence[Photon], list_comp:Callable=lambda _: None):
    q_received, photons_received = __separate_seq__(indices=indices, lst=lst)
    received_entity = "".join(list_comp(photons_received) or [str(Photon.measure(basis=photon.name, photon=photon)) for photon in photons_received])

    return q_received, received_entity

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
                    "node":"node1",
                    "message":"h",
                    "userID":"1011",
                    "num_check_bits":4,
                    "num_decoy_photons":4
                },
            "receiver":
                {
                    "node":"node2",
                    "userID":"1100"
                },
            "backend":"Qutip",
            "stoptime":10e12
        }
    print("response", ip1(topology=topology, app_settings=app_settings))