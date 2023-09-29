import logging
import os
import sys
import time
from copy import deepcopy
from functools import partial
from random import sample
from typing import Any, Dict, List, Tuple

import numpy as np
from qntsim.communication.analyzer_circuits import bell_type_state_analyzer
from qntsim.communication.attack import ATTACK_TYPE, Attack
from qntsim.communication.error_analyzer import ErrorAnalyzer
from qntsim.communication.network import Network
from qntsim.communication.noise import Noise
from qntsim.communication.security_checks import (insert_check_bits,
                                                  insert_decoy_photons)
from qntsim.communication.utils import to_binary, to_characters
from qntsim.kernel.circuit import QutipCircuit
from qntsim.utils import log

# logger = logging.getLogger("main_logger.application_layer." + "ip2")

class Party:
    node: str = None
    input_messages: Dict[Tuple, str] = None
    # input_messages:Dict[int, str] = None
    userID: str = None
    received_msgs: Dict[int, str] = None

    @classmethod
    def update_params(cls, **kwargs):
        for var, val in kwargs.items():
            setattr(cls, var, val)


class Sender(Party):
    chk_bts_insrt_lctns: List[int] = None
    num_check_bits: int = None

    @classmethod
    def input_check_bits(cls, network: Network, returns: Any, receiver:'Receiver'):
        """Alice inserts random check bits into her message for estimating the integrity of the received message
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
        """
        cls._isit, messages = to_binary(cls.input_messages.get((cls.node, receiver.node)))
        cls.input_messages[(cls.node, receiver.node)] = messages
        print(cls.input_messages)
        modified_message = insert_check_bits(
            messages=list(cls.input_messages.values()),
            num_check_bits=cls.num_check_bits,
        )
        cls.chk_bts_insrt_lctns = list(modified_message)[0]
        print(modified_message)
        for key, mod_msg in zip(cls.input_messages, modified_message.values()):
            cls.input_messages[key] = mod_msg
        logging.info(f"in message by {cls.__name__}!")
        log.logger.info("Check bits inserted by sender")

    @classmethod
    def encode(cls, network: Network, returns: Any, receiver:'Receiver', noise: Dict[str, List[float]] = {}):
        """Alice encodes her message into the memory nodes associated to her. In addition, she also performs {I, 𝑍} operations on the Id keys of Bob.
            She also applied cover operations on the decoy photons send by Bob.
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
        Returns:
            cls.d_a: List of memory keys of decoy photons
        """
        print(cls.input_messages)
        cls.i_a, cls.d_a = returns[1], returns[2]
        cls.s_a = [ele for ele in returns[0] if ele not in cls.i_a]
        cls.m_a = sample(cls.s_a, k=len(cls.s_a) - len(cls.userID) // 2)
        cls.c_a = [ele for ele in cls.s_a if ele not in cls.m_a]
        ch0, ch1, i0, i1 = (
            iter(cls.input_messages.get((cls.node, receiver.node))[::2]),
            iter(cls.input_messages.get((cls.node, receiver.node))[1::2]),
            iter(cls.userID[::2]),
            iter(cls.userID[1::2]),
        )
        for s in cls.s_a:
            qtc = QutipCircuit(1)
            if int(next(ch1) if s in cls.m_a else next(i1)):
                qtc.x(0)
            if int(next(ch0) if s in cls.m_a else next(i0)):
                qtc.z(0)
            Noise.implement(noise, circuit = qtc, keys = s, quantum_manager = network.manager)
            network.manager.run_circuit(qtc, [s])
        cls.basis = np.random.randint(2, size=len(cls.i_a))
        for i, base in zip(cls.i_a, cls.basis):
            qtc = QutipCircuit(1)
            if base:
                qtc.z(0)
            Noise.implement(noise, circuit = qtc, keys = s, quantum_manager = network.manager)
            network.manager.run_circuit(qtc, [i])
        cls.cov_ops = np.random.randint(4, size=len(cls.d_a))
        for d, ops in zip(cls.d_a, cls.cov_ops):
            q, r = divmod(ops, 2)
            qtc = QutipCircuit(1)
            if r:
                qtc.x(0)
                qtc.z(0)
            if q:
                qtc.h(0)
            Noise.implement(noise, circuit = qtc, keys = s, quantum_manager = network.manager)
            network.manager.run_circuit(qtc, [d])
        logging.info(f"message by {cls.__name__}")
        log.logger.info(f"message by {cls.__name__}")
        log.logger.info("bits encoded by sender")

        return cls.d_a

    @classmethod
    def insert_new_decoy_photons(
        cls, network: Network, returns: Any, num_decoy_photons: int
    ):
        """_summary_
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
            num_decoy_photons (int): Number of decoy photons to be inserted in the sequence of keys
        Returns:
            cls.d_a: List of memory keys of decoy photons
        """
        if "-1" in returns: return returns
        cls.d_a, cls.photons_a = insert_decoy_photons(
            network=network, node_index=0, num_decoy_photons=num_decoy_photons
        )
        cls.q_a = cls.s_a + cls.i_a + cls.d_a
        logging.info(f"in key-sequence by {cls.__name__}")
        log.logger.info(f"in key-sequence by {cls.__name__}")
        log.logger.info("Inserted decoy photons by sender")
        return cls.d_a


class Receiver(Party):
    @classmethod
    def setup(cls, network: Network, returns: Any, num_decoy_photons: int, noise: Dict[str, List[float]] = {}):
        """_summary_
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
        Returns:
            seq_a (List): _description_
            i_a (List):
            cls.d_a:
        """
        seq_a, seq_b = list(zip(*[sorted(keys)
                                  for info in network._net_topo.nodes[cls.node].resource_manager.memory_manager
                                  if info.state == "ENTANGLED" and len((keys := network.manager.get(key=info.memory.qstate_key).keys)) > 1]))
        print(seq_a, seq_b)
        cls.i_b = list(seq_b[-len(cls.userID) // 2 :])
        cls.s_b = [ele for ele in seq_b if ele not in cls.i_b]
        for k, i1, i2 in zip(cls.i_b, cls.userID[::2], cls.userID[1::2]):
            qtc = QutipCircuit(1)
            if int(i2):
                qtc.x(0)
            if int(i1):
                qtc.z(0)
            Noise.implement(noise, circuit = qtc, keys = k, quantum_manager = network.manager)
            network.manager.run_circuit(qtc, [k])
        cls.d_a, cls.photons_a = insert_decoy_photons(
            network=network, node_index=1, num_decoy_photons=num_decoy_photons
        )
        cls.d_b, cls.photons_b = insert_decoy_photons(
            network=network, node_index=1, num_decoy_photons=num_decoy_photons
        )
        logging.info(f"keys for epr pairs and decoy photons by {cls.__name__}")
        log.logger.info(f"keys for epr pairs and decoy photons by {cls.__name__}")
        cls.d_b = sorted(list(set(cls.d_b) - set(cls.d_a)))

        return seq_a, list(seq_a[-len(cls.userID) // 2 :]), cls.d_a

    @staticmethod
    def decode(network: Network, returns: Any):
        """_summary_
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
        Returns:
            _type_: _description_
        """
        if "-1" in returns: return returns
        outputs = "".join(
            str(output) for outputs in returns for output in outputs.values()
        )
        outputs = "".join([str(int(network.label[0])^int(o0))+str(int(network.label[1])^int(o1)) for o0, o1 in zip(outputs[::2], outputs[1::2])])
        log.logger.info("message decoded by receiver")
        return outputs

    @classmethod
    def check_integrity(cls, network: Network, returns: Any, cls1:'Sender', threshold: float):
        """_summary_
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
            cls1 (_type_): _description_
            threshold (float): _description_
        """
        if "-1" in returns: return returns
        print(returns)
        cls.received_msgs = "".join(
            char for i, char in enumerate(returns) if i not in cls1.chk_bts_insrt_lctns
        )
        network._strings = [cls.received_msgs]
        print(cls1._isit, cls.received_msgs, network._strings)
        cls.received_msgs = to_characters(bin_strs=[cls.received_msgs], __was_binary=cls1._isit)[0]
        print(cls1._isit, cls.received_msgs, network._strings)
        err = [int(returns[pos]) ^ int(cls1.input_messages.get((cls1.node, cls.node))[pos])
               for pos in cls1.chk_bts_insrt_lctns]
        if (err_prct := sum(err) / len(err)) > threshold:
            logging.info(f"failed, err= {1 - err_prct}")

            return
        logging.info(f"passed, messages received: {cls.received_msgs}")
        log.logger.info(f"passed, messages received: {cls.received_msgs}")
        log.logger.info("Integrity checked by receiver")

class UTP:
    @classmethod
    def check_channel_security(cls, network: Network, returns: Any,
                               cls1: type, cls2: type, threshold: float,
                               noise: Dict[str, List[float]] = {}):
        """_summary_
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
            cls1 (_type_): _description_
            cls2 (_type_): _description_
            threshold (float): _description_
        """
        readout = noise.pop("readout", [0, 0])
        if "-1" in returns: return returns
        print(f"channel_security between {cls1.__name__} and {cls2.__name__}")
        keys = returns if cls1 == Sender or cls2 == Sender else cls2.d_b
        basis = cls2.photons_a if cls1 != cls or cls2 == Sender else cls2.photons_b
        cov_ops = cls1.cov_ops if cls1 != cls else [0 for _ in range(len(basis))]
        err = []
        for key, base, ops in zip(keys, basis, cov_ops):
            b_q, b_r = divmod(base, 2)
            op_q, op_r = divmod(ops, 2)
            qtc = QutipCircuit(1)
            if b_q ^ op_q:
                qtc.h(0)
            Noise.implement(noise, circuit = qtc, keys = key, quantum_manager = network.manager)
            qtc.measure(0)
            output = network.manager.run_circuit(qtc, [key])
            Noise.readout(readout, output)
            err.append(output.get(key) ^ b_r ^ op_r)
        mean_ = sum(err) / len(err)
        if mean_ >= threshold:
            logging.info(
                f"failed between {cls1.__name__} and {cls2.__name__}, err={mean_}"
            )
            # sys.exit(f"failed between {cls1.__name__} and {cls2.__name__}, err={mean_}")
            return {"-1":f'failed between {cls1.__name__} and {cls2.__name__}, err={np.mean(err)}'}
            # os._exit(f'Security of the channel between {cls1.__name__} and {cls2.__name__} is compromised.')
        logging.info(f"passed between {cls1.__name__} and {cls2.__name__}")
        log.logger.info(f"passed between {cls1.__name__} and {cls2.__name__}")
        log.logger.info("Channel security checked by UTP")
        return returns

    @staticmethod
    def authenticate(network: Network, returns: Any,
                     cls1: type, cls2: type, circuit: QutipCircuit,
                     noise: Dict[str, List[float]] = {}):
        """_summary_
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
            cls1 (_type_): _description_
            cls2 (_type_): _description_
            circuit (QutipCircuit): _description_
        Returns:
            _type_: _description_
        """
        if "-1" in returns: return returns
        outputs = []
        for ia, ib in zip(cls1.i_a, cls2.i_b):
            state = network.manager.get(ia)
            output: Dict[int, int] = network.manager.run_circuit(circuit, state.keys)
            Noise.readout(noise.get("readout", [0, 0]), output)
            outputs.extend(list(output.values()))
        outputs = "".join(
            str(output) if i % 2 else str(output ^ cls1.basis[i // 2])
            for i, output in enumerate(outputs)
        )
        # outputs = "".join([str(int(o)^int(b)) for o, b in zip(outputs, network.label+network.label)])
        outputs = "".join([str(int(network.label[0])^int(o0))+str(int(network.label[1])^int(o1)) for o0, o1 in zip(outputs[::2], outputs[1::2])])
        print("1", outputs)
        if outputs != cls2.userID:
            raise Exception(f"{cls2.__name__} is not authenticated")
        else:
            logging.info(f"{cls2.__name__}, passed!")
            # logger.info(f"{cls2.__name__}, passed!")
        outputs = []
        for c in cls1.c_a:
            state = network.manager.get(c)
            output: Dict[int, int] = network.manager.run_circuit(circuit, state.keys)
            Noise.readout(noise.get("readout", [0, 0]), output)
            outputs.extend(list(output.values()))
        # outputs = "".join([str(int(o)^int(b)) for o, b in zip(outputs, network.label+network.label)])
        outputs = "".join([str(int(network.label[0])^int(o0))+str(int(network.label[1])^int(o1)) for o0, o1 in zip(outputs[::2], outputs[1::2])])
        print("2", outputs)
        if outputs != cls1.userID:
            raise Exception(f"{cls1.__name__} is not authenticated")
        else:
            logging.info(f"{cls1.__name__}, passed!")
            log.logger.info(f"{cls1.__name__}, passed!")
            log.logger.info("Channle authenticated by UTP")

        return outputs

    @staticmethod
    def measure(network: Network, returns: Any, circuit: QutipCircuit,
                cls: type, noise: Dict[str, List[float]] = {}):
        """_summary_
        Args:
            network (Network): The <Network> instance which executes the sequence of functions
            returns (Any): Returns from the previous function in the sequence
            circuit (QutipCircuit): _description_
        Returns:
            _type_: _description_
        """
        if "-1" in returns: return returns
        outputs = []
        for m in cls.s_a:
            if m in cls.m_a:
                state = network.manager.get(m)
                output: Dict[int, int] = network.manager.run_circuit(circuit, state.keys)
                Noise.readout(noise.get("readout", [0, 0]), output)
                outputs.extend(list(output.values()))
        log.logger.info("measurement performed by UTP")
        return outputs


def pass_(network: Network, returns: Any):
    return returns



def ip2_run(topology: Dict[str, Any], app_settings: Dict[str, Any], noise: Dict[str, List[float]] = {}):
    message = app_settings.get("sender").get("message")
    app_settings.get("sender").update(
        {
            "input_messages": {
                (
                    app_settings.get("sender").get("node"),
                    app_settings.get("receiver").get("node"),
                ): message
            }
        }
    )
    Sender.update_params(**(app_settings.get("sender")))
    Receiver.update_params(**(app_settings.get("receiver")))
    label = app_settings.get("bell_type", "00")
    error_threshold = app_settings.get("error_threshold", 0.5)
    attack = app_settings.get("attack")
    channel = app_settings.get("channel")
    channel = [1 if i+1 == channel else 0 for i in range(3)]
    print(attack, channel)
    Network._flow = [
        # partial(Network.draw),
        # partial(Network.dump),
        partial(Sender.input_check_bits, receiver=Receiver),
        partial(Receiver.setup, num_decoy_photons=Sender.num_decoy_photons, noise = deepcopy(noise)),
        partial(Sender.encode, receiver=Receiver, noise = deepcopy(noise)),
        partial(Attack.implement, attack=ATTACK_TYPE[attack].value)
        if attack in ATTACK_TYPE.__members__ and channel[0]
        else partial(pass_),
        partial(UTP.check_channel_security,
                cls1=Sender,
                cls2=Receiver,
                threshold=error_threshold,
                noise = deepcopy(noise)),
        partial(Sender.insert_new_decoy_photons, num_decoy_photons=Sender.num_decoy_photons),
        #  partial(Attack.implement, attack=ATTACK_TYPE[attack].value) if attack and chnnl[1] else partial(pass_),
        partial(UTP.check_channel_security,
                cls1=UTP,
                cls2=Sender,
                threshold=error_threshold,
                noise = deepcopy(noise)),
        partial(Attack.implement, attack=ATTACK_TYPE[attack].value)
        if attack in ATTACK_TYPE.__members__ and channel[2]
        else partial(pass_),
        partial(UTP.check_channel_security,
                cls1=UTP,
                cls2=Receiver,
                threshold=error_threshold,
                noise = deepcopy(noise)),
        partial(UTP.authenticate,
                cls1=Sender,
                cls2=Receiver,
                circuit=bell_type_state_analyzer(2),
                noise = deepcopy(noise)),
        partial(UTP.measure,
                circuit=bell_type_state_analyzer(2),
                cls=Sender,
                noise = deepcopy(noise)),
        partial(Receiver.decode),
        partial(Receiver.check_integrity, cls1=Sender, threshold=error_threshold),
    ]
    network = Network(
        topology=topology,
        messages=Sender.input_messages,
        name="ip2",
        size=lambda x: (
            x + Sender.num_check_bits + len(Sender.userID) + len(Receiver.userID)
        )
        // 2,
        label=label,
    )
    start_time = time.time()
    err_msg = network()
    end_time = time.time()
    # print(network._bin_msgs, network._strings)
    if not err_msg:
        err_tuple = ErrorAnalyzer._analyse(network=network)
        print(f"Average error in network:{err_tuple[2]}")
        print(f"Standard deviation in error in network:{err_tuple[3]}")
        print(f"Information leaked to the attacker:{err_tuple[4]}")
        print(f"Fidelity of the message:{err_tuple[5]}")
        # Network.execute(networks=[network])
        print('Received messages:', Receiver.received_msgs)

        app_settings.update(
            output_msg=Receiver.received_msgs,
            avg_err=err_tuple[2],
            std_dev=err_tuple[3],
            info_leak=err_tuple[4],
            msg_fidelity=err_tuple[5],
        )
    else: app_settings.update({"Err_msg":err_msg.get("-1", "Unidentified error.")})
    app_settings.get("sender").pop("input_messages")
    # app_settings.get("sender")["userID"] = to_string(strings=[app_settings.get("sender").get("userID")], _was_binary=_is_sender)[0]
    # app_settings.get("receiver")["userID"] = to_string(strings=[app_settings.get("receiver").get("userID")], _was_binary=_is_receiver)[0]
    response = {}
    response["application"] = app_settings
    print(response)
    from main.simulator.topology_funcs import network_graph

    # from ..topology_funcs import network_graph
    response = network_graph(
        network_topo=network._net_topo, source_node_list=[Sender.node], report=response
    )
    response["performance"]["execution_time"] = end_time - start_time

    # return network, Receiver.received_msgs, err_tuple[2:]
    return response

if __name__ == "__main__":
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
            
    app_settings = {
            "sender": {
                "message": "011011",
                "node": "node1",
                "userID": "1001",
                "num_check_bits": 4,
                "num_decoy_photons": 4,
            },
            "receiver": {"node": "node2", "userID": "0110"},
            "attack":"none",
            "channel":1,
            "error_threshold": 0.4,
            "bell_type": "01",
        }
    response = ip2_run(topology=topology, app_settings=app_settings)

    print(response)