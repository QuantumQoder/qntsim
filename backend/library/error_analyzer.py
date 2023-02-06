import numpy as np, matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor
from numpy.random import randint
from statistics import mean, stdev

from .network import Network

class ErrorAnalyzer:
    from .protocol import Protocol
    
    @staticmethod
    def analyse(protocol:Protocol):
        def _analyse(i:int, network:Network):
            messages = network.messages
            strings = network.strings
            err_list = np.zeros(len(messages[0]))
            for message, string in zip(messages, strings):
                err_list+=np.array([int(m)^int(s) for m, s in zip(message, string)])
            err_list/=len(messages)
            err_prct = mean(err_list)*100
            err_sd = stdev(err_list)
            print(f'Avg. err. for iter. {i}: {err_prct}')
            print(f'Deviation in err. for iter. {i}: {err_sd}')
            
            return err_list.tolist(), err_prct, err_sd
        networks = protocol.networks
        results = ProcessPoolExecutor().map(_analyse, enumerate(networks, 1))
        full_err_list, mean_list, sd_list = tuple(zip(*results))
        
        return full_err_list, mean_list, sd_list
    
    @staticmethod
    def run_full_analysis(type:int, num_iterations:int, message_length:int, *args, **kwargs):
        from .protocol import Protocol
        
        messages_list = [[''.join(str(ele) for ele in randint(2, size=message_length)) for _ in range(type)] for _ in range(num_iterations)]
        protocol = Protocol(*args, **kwargs, messages_list=messages_list)
        full_err_list, mean_list, sd_list = protocol.full_err_list, protocol.mean_list, protocol.sd_list
        attack = kwargs.get('attack', 'no')
        print(f'Error analysis for {attack} attack')
        bit_error = sum(full_err_list)
        plt.figure(figsize=(20, 5))
        plt.bar(range(len(bit_error)), bit_error)
        plt.xlabel('Bits')
        plt.ylabel(f'Error per bit for {num_iterations} iterations')
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
        print(f'Total error over all the bits for {num_iterations} iterations: {mean(bit_error)}')
        print(f'Total mean error over all the {num_iterations} iterations: {mean(mean_list)}')
        print(f'Total error deviation over all the {num_iterations} iterations: {mean(sd_list)}')