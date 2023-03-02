import numpy as np, matplotlib.pyplot as plt, logging
from joblib import Parallel, wrap_non_picklable_objects, delayed
from numpy.random import randint
from statistics import mean, stdev

from .network import Network

class ErrorAnalyzer:
    @staticmethod
    # @delayed
    # @wrap_non_picklable_objects
    def _analyse(i:int, network:Network):
        err_list = np.zeros(len(network.bin_msgs[0]))
        for bin_msg, string in zip(network.bin_msgs, network.strings[::-1]):
            err_list+=np.array([int(m)^int(s) for m, s in zip(bin_msg, string)])
        err_list/=len(network.bin_msgs)
        err_prct = mean(err_list)*100
        err_sd = stdev(err_list)
        logging.info(f'Avg. err. for iteration {i}: {err_prct}')
        logging.info(f'Deviation in err. for iteration {i}: {err_sd}')
        
        return err_list, err_prct, err_sd
    
    from .protocol import Protocol    
    @classmethod
    def analyse(cls, protocol:Protocol):
        return [cls._analyse(i, network) for i, network in enumerate(protocol, 1)]
        # return Parallel(n_jobs=-1, prefer='threads') (cls._analyse(i, network) for i, network in enumerate(protocol, 1))
    
    @staticmethod
    def run_full_analysis(type_:int, num_iterations:int, message_length:int, **kwds):
        from .protocol import Protocol
        
        messages_list = [{i:''.join(str(ele) for ele in randint(2, size=message_length)) for i in range(type_)} for _ in range(num_iterations)]
        protocol = Protocol(**kwds, messages_list=messages_list)
        protocol(**kwds)
        full_err_list, mean_list, sd_list = protocol.full_err_list, protocol.mean_list, protocol.sd_list
        attack = kwds.get('attack', 'no')
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