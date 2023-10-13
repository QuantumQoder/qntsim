from statistics import mean, stdev
from typing import List, Optional, Tuple

import numpy as np

from ..log_functions import log_info
from ..types import Types
from .utils import to_characters


class ErrorAnalyzer:
    @staticmethod
    def analysis(bin_list1: List[str], bin_list2: List[str], leaked_bins: Optional[List[str]] = None, count: int = 0) -> Tuple[np.ndarray, np.ndarray, float, float, float, float]:
        error_list = np.zeros(bin_list1[0])
        leaked_list = np.zeros(bin_list1[0])
        for bin_str1, bin_str2 in zip(bin_list1, bin_list2):
            error_list += np.array([int(b1) ^ int(b2) for b1, b2 in zip(bin_str1, bin_str2)])
        for leaked_bin in leaked_bins: leaked_list += np.array(leaked_bin)
        error_list /= len(bin_list1)
        leaked_list /= len(bin_list1)
        mean_error: float = mean(error_list) * 100
        dev_error: float = stdev(error_list)
        mean_leakge: float = mean(leaked_list) * 100
        log_info(f"Avg. error for iteration {count}: {mean_error}")
        log_info(f"Deviation for iteration {count}: {dev_error}")
        log_info(f"Message fidelity retained: {100-mean_error}")
        log_info(f"{mean_leakge}% info leaked to attacker")
        return error_list, leaked_list, mean_error, 100 - mean_error, dev_error, mean_leakge

    from .qntsimulation import QNtSimulation
    @classmethod
    def simulation_analysis(cls, simulation: QNtSimulation) -> Types.messages:
        for binary_packet in simulation.binary_packets:
            output_message = binary_packet.get("output_message", {})
            input_message = [package.get("message", "") for key, package in binary_packet.items() if key != "output_message"]
            _, _, mean_error, msg_fidelity, dev_error, mean_leakage = cls.analysis(input_message, list(output_message.values()))
            binary_packet.update(mean_error = mean_error,
                                 msg_fidelity = msg_fidelity,
                                 dev_error = dev_error,
                                 mean_leakage = mean_leakage)
        simulation.received_messages = to_characters(simulation.binary_packets)
        return simulation.received_messages

    def auto_analyse():
        pass

# class ErrorAnalyzer:
#     @staticmethod
#     # @delayed
#     # @wrap_non_picklable_objects
#     def _analyse(network: Network, i: int = 0):
#         err_list = np.zeros(len(network._bin_msgs[0]))
#         lk_list = np.zeros(len(network._bin_msgs[0]))
#         print(network._bin_msgs, network._strings)
#         for bin_msg, string in zip(network._bin_msgs, network._strings[::-1]):
#             err_list += np.array([int(m) ^ int(s) for m, s in zip(bin_msg, string)])
#             lk_list += np.array(
#                 [
#                     int(m) ^ int(lk)
#                     for m, lk in zip(
#                         bin_msg,
#                         network._lk_msg if hasattr(network, "_lk_msgs") else bin_msg,
#                     )
#                 ]
#             )
#         err_list /= len(network._bin_msgs)
#         lk_list /= len(network._bin_msgs)
#         err_prct = mean(err_list) * 100
#         err_sd = stdev(err_list)
#         info_lk = mean(lk_list) * 100
#         logging.info(f"Avg. err. for iteration {i}: {err_prct}%")
#         logging.info(f"Deviation in err. for iteration {i}: {err_sd}")
#         logging.info(f"Fidelity of the message retained: {100-err_prct}%")
#         logging.info(f"{info_lk}% info leaked to the attacker.")

#         return err_list, lk_list, err_prct, err_sd, info_lk, 100 - err_prct

#     from .protocol import ProtocolPipeline

#     @classmethod
#     def analyse(cls, protocol: ProtocolPipeline):
#         """Analyse the networks present in protocol

#         Args:
#             protocol (Protocol): <Protocol> object

#         Returns:
#             _type_: _description_
#         """
#         return list(
#             zip(*[cls._analyse(network, i=i) for i, network in enumerate(protocol, 1)])
#         )
#         # return Parallel(n_jobs=-1, prefer='threads') (cls._analyse(i, network) for i, network in enumerate(protocol, 1))

#     @staticmethod
#     def run_full_analysis(type_: int, num_iterations: int, message_length: int, **kwds):
#         """Runs full analysis over the network

#         Args:
#             type_ (int): The type of protocol. QSDC is 0
#             num_iterations (int): Total number of iterations to run through
#             message_length (int): The length of the message
#         """
#         from .protocol import ProtocolPipeline

#         messages_list = [
#             {
#                 i: "".join(str(ele) for ele in randint(2, size=message_length))
#                 for i in range(type_)
#             }
#             for _ in range(num_iterations)
#         ]
#         protocol = ProtocolPipeline(**kwds, messages_list=messages_list)
#         protocol(**kwds)
#         attack = kwds.get("attack", "no")
#         print(f"Error analysis for {attack} attack")
#         bit_error = sum(protocol.full_err_list)
#         bit_lk = sum(protocol.full_lk_list)
#         plt.figure("Error per bit", figsize=(20, 5))
#         plt.bar(range(len(bit_error)), bit_error)
#         plt.xlabel("Bits")
#         plt.ylabel(f"Error per bit for {num_iterations} iterations")
#         plt.show()
#         plt.figure("Info. leakage per bit", figsize=(20, 5))
#         plt.bar(range(len(bit_lk)), bit_lk)
#         plt.xlabel("Bits")
#         plt.ylabel(f"Info. leak per bit for {num_iterations} iterations")
#         plt.show()
#         plt.figure("Error per iteration", figsize=(20, 5))
#         plt.plot(range(len(protocol.mean_list)), protocol.mean_list)
#         plt.xlabel("Number of iterations")
#         plt.ylabel("Mean error per iteration")
#         plt.show()
#         plt.figure("Deviation in error per iteration", figsize=(20, 5))
#         plt.plot(range(len(protocol.sd_list)), protocol.sd_list)
#         plt.xlabel("Number of iterations")
#         plt.ylabel("Mean deviation in error per iteration")
#         plt.show()
#         plt.figure("Info. leakege per iteration", figsize=(20, 5))
#         plt.plot(range(len(protocol.lk_list)), protocol.lk_list)
#         plt.xlabel("Number of iterations")
#         plt.ylabel("Mean info. leakage per iteration")
#         plt.show()
#         plt.figure("Fidelity of message per iteration", figsize=(20, 5))
#         plt.plot(range(len(protocol.fid_list)), protocol.fid_list)
#         plt.xlabel("Number of iterations")
#         plt.ylabel("Mean fidelity per iteration")
#         plt.show()
#         print(
#             f"Avg. error over all the bits for {num_iterations} iterations: {mean(bit_error)}"
#         )
#         print(
#             f"Avg. info. leakage over all the bits for {num_iterations} iterations: {mean(bit_lk)}"
#         )
#         print(
#             f"Avg. mean error over all the {num_iterations} iterations: {mean(protocol.mean_list)}"
#         )
#         print(
#             f"Avg. error deviation over all the {num_iterations} iterations: {mean(protocol.sd_list)}"
#         )
#         print(
#             f"Avg. info. leakage over all the {num_iterations} iterations: {mean(protocol.lk_list)}"
#         )
#         print(
#             f"Avg. fidelity over all the {num_iterations} iterations: {mean(protocol.fid_list)}"
#         )
