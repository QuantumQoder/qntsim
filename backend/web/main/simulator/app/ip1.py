import time
from math import inf
from statistics import mean
from typing import Any, Callable, Dict, Sequence

import numpy as np
from pandas import DataFrame
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
from rich import print_json
from rich_dataframe import prettify
from rich_dataframe import print as print_rich

basis = polarization.get("bases")

def ip1(topology:Dict, app_settings:Dict[str, Dict[str, Any]]):
    response = {}
    theta = app_settings.get("theta", np.random.randint(0, 360)) # If user doesn't provide value, default it to numpy.randint
    message = app_settings.get("sender").get("message")
    _is_binary, messages = to_binary(messages=[message])

    # #####################################################       Setting up the simulator         #################################################
    start_time = time.time()
    simulator = Timeline( stop_time=app_settings.get("stop_time", inf), backend=app_settings.get("backend", "Qutip"))
    configuration = Topology(name="ip1", timeline=simulator)
    configuration.load_config_json(config=topology)
    logger.debug("loaded topology into the simulator")
    src_node:EndNode = configuration.nodes.get(app_settings.get("sender").get("node"))
    dst_node:EndNode = configuration.nodes.get(app_settings.get("receiver").get("node"))

    logger.info("|------------------Simulation started------------------|")
    mod_msg = insert_check_bits(messages=messages, num_check_bits=(num_check_bits:=app_settings.get("sender").get("num_check_bits")))
    logger.debug(f"{num_check_bits} check bits inserted into the message")

    # ############################################      Encoding user input message into photons           ########################################
    logger.info("|---------------Encoding process started---------------|")
    print(mod_msg)
    photons = [Photon(name="msg"+str(char), quantum_state=basis[0][int(char)]) for _, message in mod_msg.items() for char in message]
    logger.info("Message encoded into the photons")
    logger.debug("Message photons generated")
    wp = Waveplate(name=theta, timeline=simulator, angle=theta)
    photons = [wp.apply(qubit=photon) for photon in photons]
    logger.debug(f"Applied {theta}\degree rotation to the message photons")
    
    # #########################################              Encoding sender's id into photons           #################################
    sender_id = app_settings.get("sender").get("userID")
    ids_photons = [Photon(name="ids"+str(i0), quantum_state=basis[int(i0)][int(i1)]) for i0, i1 in zip(sender_id[::2], sender_id[1::2])]
    logger.info(f"Sender ID {sender_id} encoded into the photons")

    # ###################################                   Encoding receiver's id into photons             ################################
    receiver_id = app_settings.get("receiver").get("userID")
    r = np.random.randint(low=0, high=2, size=len(receiver_id))
    idr_photons = [Photon(name="idr"+str(i0), quantum_state=basis[int(i0)][int(i0)^int(i1)]) for i0, i1 in zip(receiver_id, r)]
    logger.info(f"Receiver ID {receiver_id} encoded into the photons")

    # ########################################             Encoding rotation angle into photons           #############################
    theta_bin = bin(theta)[2:].rjust(9, '0')
    print("Theta", theta_bin, bin(theta))
    theta_photons = [Photon(name="theta"+str(i0), quantum_state=basis[int(i0)][int(i1)]) for i0, i1 in zip(receiver_id, '0'*(len(receiver_id)-len(theta_bin))+theta_bin)]

    # ###########################################   Generating decoy photons for security checking            ##########################
    decoy_states = np.random.randint(4, size=app_settings.get("sender").get("num_decoy_photons"))
    prettify(DataFrame(decoy_states), clear_console=False)
    decoy_photons = [Photon(name="decoy"+str(state//2), quantum_state=basis[state//2][state%2]) for state in decoy_states]
    logger.info(f"{len(decoy_states)} decoy photons generated")
    logger.debug("Constructing photon sequence")
    ids_locs, q2 = __insert_seq__(photons, ids_photons) # q1 + ids
    idr_locs, q3 = __insert_seq__(q2, idr_photons) # q2 + idr
    theta_locs, q4 = __insert_seq__(q3, theta_photons) # q3 + theta
    decoy_locs, q5 = __insert_seq__(q4, decoy_photons) # q4 + decoy
    for photon in q5:
        photon.name = str(q5.index(photon))+" "+photon.name
        simulator.events.push(event=Event(time=simulator.now()+time.time(), owner=src_node, activation_method="send_qubit", act_params=[dst_node.name, photon]))
        logger.debug(f"Generated event for sending qubit to {dst_node.name} node")
    simulator.init()
    simulator.run()
    simulator.is_running = True
    photons_received = dst_node.qubit_buffer.get(1, []) # received photons at the receiver's node
    rearranged_photons = rearrange_photons(photons=photons_received) # q5
    print("photons received:")
    prettify(DataFrame({"send photons":q5, "recieved photons":rearranged_photons}), clear_console=False, row_limit=100, col_limit=50)
    logger.info(f"Photons received at {dst_node.name} node")

    logger.info("|--------------Extraction and Decoding started------------|")

    print("q4")
    q4_received, received_decoy_meas = extract_seq(indices=decoy_locs, lst=rearranged_photons) # q5 - decoy
    logger.info("Extracted decoy photons")
    if mean([int(state%2)^int(recv_meas) for state, recv_meas in zip(decoy_states, received_decoy_meas)]) > app_settings.get("err_threshold", 0.25):
        logger.info("Eavesdropper detected in channel")
        return
    rearranged_q4 = rearrange_photons(photons=q4_received)
    prettify(DataFrame(rearranged_q4), clear_console=False, row_limit=100)
    
    print("q3")
    q3_received, received_theta_str = extract_seq(indices=theta_locs, lst=rearranged_q4) # q4 - theta
    rearranged_q3 = rearrange_photons(photons=q3_received)
    prettify(DataFrame(rearranged_q3), clear_console=False, row_limit=100)
    
    print("q2")
    q2_received, received_receiver_id = extract_seq(indices=idr_locs, lst=rearranged_q3) # q3 - idr
    rearranged_q2 = rearrange_photons(photons=q2_received)
    prettify(DataFrame(rearranged_q2), clear_console=False, row_limit=100)
    # prettify(DataFrame([ids_locs, idr_locs, theta_locs, decoy_locs]), clear_console=False)
    logger.info("Extracted receiver id")
    if mean([int(r_id!=s_id)^r for r_id, s_id, r in zip(received_receiver_id, receiver_id, r)]) > 0.3:
        print("returned")
        logger.info("Receiver not authenticated")
        return
    
    print("q1")
    q1_received, received_sender_id = extract_seq(indices=ids_locs, lst=rearranged_q2, list_comp=lambda photons: [str(Photon.measure(basis=basis[int(photon.name[-1])], photon=photon)) for photon in photons]) # q2 - ids
    rearranged_q1 = rearrange_photons(photons=q1_received)
    prettify(DataFrame(rearranged_q1), clear_console=False, row_limit=100)
    logger.info("Extracted sender id")
    if mean([int(r_id==s_id) for r_id, s_id in zip(received_sender_id, sender_id)]) > 0.3:
        logger.info("Sender not authenticated")
        return
    received_theta = int(received_theta_str, 2)
    logger.info("recovered rotation angle from photon sequence received")
    wp = Waveplate(name="-"+str(received_theta), timeline=simulator, angle=-received_theta)
    # prettify(DataFrame([wp.apply(qubit=photon) for photon in rearranged_q1]), clear_console=False)
    # prettify(DataFrame([Photon.measure(basis=basis[0], photon=wp.apply(qubit=photon)) for photon in rearranged_q1]), clear_console=False)
    mod_q1 = "".join([str(Photon.measure(basis=basis[0], photon=wp.apply(qubit=photon))) for photon in rearranged_q1])
    print(mod_msg)
    print(mod_q1)
    for positions in mod_msg:
        recv_msg, received_check_bits = __separate_seq__(indices=positions, lst=mod_q1)
        if (msg_integrity := mean([int(mod_q1[index]!=chk_bit) for index, chk_bit in zip(positions, received_check_bits)])) > 0.3:
            logger.info(f"Integrity of the message is compromised: {msg_integrity}%")
            return
        break
    simulator.is_running = False
    logger.info(f"|-------------Simulation Completed!! Message has been safely transferred from {src_node.name} to {dst_node.name}----------------------|")

    recv_msg = "".join(char for char in recv_msg)
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
    print("RESPONSE")
    print_json(data=response)
    from main.simulator.topology_funcs import network_graph
    response = network_graph(network_topo=configuration, source_node_list=[src_node.name], report=response)
    response["performance"]["execution_time"] = end_time - start_time

    return response

def extract_seq(indices:Sequence[int], lst:Sequence[Photon], list_comp:Callable=lambda _: None):
    q_received, photons_received = __separate_seq__(indices=indices, lst=lst)
    print_rich(photons_received)
    results = list_comp(photons_received) or [str(Photon.measure(basis=basis[int(photon.name[-1])], photon=photon)) for photon in photons_received]
    received_entity = "".join(results)

    return q_received, received_entity

def rearrange_photons(photons:Sequence[Photon]):
    rearranged_photons = {int(photon.name.split()[0]):photon for photon in photons}
    rearranged_photons = [rearranged_photons[index] for index in sorted(rearranged_photons)]

    return rearranged_photons

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
                    "userID":"1011110010",
                    "num_check_bits":4,
                    "num_decoy_photons":4
                },
            "receiver":
                {
                    "node":"node2",
                    "userID":"110011001"
                },
            "backend":"Qutip",
            "stoptime":10e12
        }
    ip1(topology=topology,
        app_settings=app_settings)
    # print_json({"response":ip1(topology=topology,
    #                            app_settings=app_settings)})