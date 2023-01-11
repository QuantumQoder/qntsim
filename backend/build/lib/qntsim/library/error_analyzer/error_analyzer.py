from statistics import mean, stdev
from numpy.random import randint
import numpy as np, matplotlib.pyplot as plt

def ignore(obj):
    def _():
        pass
    return _

class ErrorAnalyzer:
    from qntsim.library.protocol_handler.protocol_handler import Protocol
    
    @staticmethod
    def analyse(protocol_obj:Protocol):
        platform = protocol_obj.platform
        networks = protocol_obj.networks
        full_err_list, mean_list, sd_list = [], [], []
        for i, network in enumerate(networks, 1):
            messages = network.messages
            strings_list = network.strings[::-1]
            err_list, prob_list = np.zeros(len(messages[0])), np.array([0])
            for message, string in zip(messages, strings_list):
                if platform=='qiskit':
                    for key, prob in string.items():
                        np.append([err_list], [[int(m)^int(s) for m, s in zip(message, key)]])
                        np.append(prob_list, prob)
                else:
                    err_list+=np.array([int(m)^int(s) for m, s in zip(message, string)])
            err_list = err_list[1:].T@prob_list if platform=='QISKIT' else err_list/len(messages)
            err_prct = mean(err_list)*100
            err_sd = stdev(err_list)
            full_err_list.append(err_list.tolist())
            mean_list.append(err_prct)
            sd_list.append(err_sd)
            print(f'Average error for iteration {i}: {err_prct}')
            print(f'Deviation in the error for {i}: {err_sd}')
        
        return full_err_list, mean_list, sd_list
    
    def run_full_analysis(type:int, iterations:int, message_length:int, **kwargs):
        from ..protocol_handler.protocol_handler import Protocol
        
        attack = kwargs.get('attack', 'no')
        messages_list = [[''.join(str(ele) for ele in randint(2, size=message_length)) for _ in range(type)] for _ in range(iterations)]
        protocol = Protocol(kwargs, messages_list=messages_list)
        full_err_list, mean_list, sd_list = protocol.full_err_list, protocol.mean_list, protocol.sd_list
        print(f'Error analysis for {attack} attack')
        bit_error = sum(full_err_list)
        plt.figure(figsize=(20, 5))
        plt.bar(range(len(bit_error)), bit_error)
        plt.xlabel('Bits')
        plt.ylabel(f'Error per bit for {iterations} iterations')
        plt.show()
        plt.figure(figsize=(20, 5))
        plt.plot(range(len(mean_list)), mean_list)
        plt.xlabel('Number of iterations')
        plt.ylabel('Mean error per iteration')
        plt.show()
        plt.figure(figsize=(20, 5))
        plt.plot(range(len(sd_list)), sd_list)
        plt.xlabel('Number of iterations')
        plt.ylabel('Mean deviation in error per iteration')
        plt.show()
        print(f'Total error over all the bits for {iterations} iterations: {mean(bit_error)}')
        print(f'Total mean error over all the {iterations} iterations: {mean(mean_list)}')
        print(f'Total error deviation over all the {iterations} iterations: {mean(sd_list)}')