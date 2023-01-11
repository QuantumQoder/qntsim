from statistics import mean, stdev
import numpy as np

def ignore(obj):
    def _():
        pass
    return _

class ErrorAnalyzer:
    from ..protocol_handler.protocol_handler import Protocol
    
    @staticmethod
    def analyse(protocol_obj:Protocol):
        networks = protocol_obj.networks
        full_err_list, mean_list, sd_list = [], [], []
        for i, network in enumerate(networks, 1):
            platform = network.platform
            messages = network.messages
            strings_list = network.strings[::-1]
            err_list, prob_list = np.zeros(len(messages[0])), np.array([])
            for message, string in zip(messages, strings_list):
                if platform=='QISKIT':
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