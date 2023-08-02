'''
This file contains different noises, their description and python code to realize them.
Here following noises are included:
i. SPAM (State Preparation And Measurement)
'''

from enum import Enum
from numbers import Number
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .Error import NoiseError

_ATOL = 1e-6

def check_probability(probabilities:List[Number], tolerance:Number) -> None:
    
    '''
    Check whether probabilities are valid or not (upto given tolerance).
    '''
    
    if not isinstance(probabilities, list):
        raise NoiseError("Probabilities should be a list")
    if not probabilities:
        raise NoiseError("Input probabilities: Empty")
    for p in probabilities:
        if isinstance(p, int) or isinstance(p, float):
            if p < -tolerance or p > 1 + tolerance:
                raise NoiseError(f"Probability {p} does not lie in the interval [0, 1]")
        else:
            raise NoiseError(f"Probability {p} is not a real number")
    if abs(sum(probabilities) - 1) > tolerance:
        raise NoiseError(f"Sum of the probabilities {probabilities} is not 1")
    pass

def scale_probability(probabilities:Sequence[Number]) -> Sequence[Number]:
    
    '''
    Scales the probability values in proper range
    '''
    
    for i in range(len(probabilities)):
        if probabilities[i] < 0:
            probabilities[i] = 0
        if probabilities[i] > 1:
            probabilities[i] = 1
    s = sum(probabilities)
    if s - 1:
        for i in range(len(probabilities)):
            probabilities[i] /= s
    return probabilities

class ReadoutError:
    
    '''
    Readout error can be caracterised by following components:
    
    i. Probability of getting 0 when ideal measurement gives 0
    
    ii. Probability of getting 1 when ideal measurement gives 0
    
    iii. Probability of getting 0 when ideal measurement gives 1
    
    iv. Probability of getting 1 when ideal measurement gives 1
    
    Note that if 2nd and 3rd probability is given then other two probabilities can be found by
    subtracting them from 1.
    '''
    
    def __init__(self, p01:Number, p10:Number) -> None:
        '''
        Create a readout error for noise model
        
        Inputs:
            p01 [double]: Probability of getting 1 when ideal measurement gives 0
            p10 [double]: Probability of getting 0 when ideal measurement gives 1
        '''
        
        check_probability(probabilities = [p01, 1 - p01], tolerance = _ATOL)
        check_probability(probabilities = [p10, 1 - p10], tolerance = _ATOL)
        self.ideal = False
        if p01 + p10 < _ATOL:
            self.ideal = True
        self.probabilities = [scale_probability([1 - p01, p01]), scale_probability([p10, 1 - p10])]
        pass

class ResetError:
    
    '''
    Reset error can be characterised by following components:
    
    i. With probability :math:`p_0` qubit is reset to :math:`\\vert 0 \\rangle`
    
    ii. With probability :math:`p_1` qubit is reset to :math:`\\vert 1 \\rangle`
    
    iii. With probability :math:`1 - p_0 - p_1` no reset happens
    
    Therefore the error map will be :math:`E(\\rho) = (1 - p_0 - p_1) \\rho + \\left(p_0 \\vert 0 \\rangle\\langle 0 \\vert + p_1 \\vert 1 \\rangle\\langle 1 \\vert\\right)`
    '''
    
    def __init__(self, p0:Number, p1:Number) -> None:
        
        '''
        Create a reset error for noise model 
        
        Inputs:
            p0 [double]: Probability of resetting to :math:`\\vert 0 \\rangle`
            p1 [double]: Probability of resetting to :math:`\\vert 1 \\rangle`
        '''
        
        check_probability(probabilities = [p0, p1, 1 - p0 - p1], tolerance = _ATOL)
        self.ideal = False
        if abs(p0 - 1) < _ATOL:
            self.ideal = True
        self.probabilities = scale_probability([1 - p0 - p1, p0, p1])
        pass

class PauliError:

    '''
    Pauli error can be characterized by following components:
    
    i. With probability :math:`p_I` identity will be applied
    
    ii. With probability :math:`p_X` Pauli :math:`X` will be applied
    
    iii. With probability :math:`p_Z` Pauli :math:`Z` will be applied
    
    iv. With probability :math:`p_Y` Pauli :math:`Y (= ZX)` will be applied
    
    Therefore the error map will be :math:`E(\\rho) = p_I \\rho + p_X X \\rho X + p_Z Z \\rho Z + p_Y ZX \\rho XZ`
    '''
    
    def __init__(self, err_prob:Union[List[Union[Tuple, Number]], Dict[str, Number]]) -> None:
    
        '''
        Create a Pauli error for noise model
        
        Input:
            err_prob [list or dictionary]: Probability for Pauli gates to apply. :math:`[p_I, p_X, p_Y, p_Z]` or :math:`\\{'P':p_P\\}` or :math:`[('P',p_P)]` for Pauli operator :math:`P` and corresponding probability :math:`p_P`.
        '''
        
        probabilities = []
        Pauli = ['I', 'X', 'Y', 'Z']
        if isinstance(err_prob, list):
            err_dict = {}
            flag = None
            for p in err_prob:
                if isinstance(p, tuple):
                    if flag == 0:
                        raise NoiseError('Error input should be either list of float or list of tuples, not both.')
                    else:
                        flag = 1
                        err_dict[p[0]] = p[1]
                else:
                    if flag == 1:
                        raise NoiseError('Error input should be either list of float or list of tuples, not both.')
                    else:
                        flag = 0
            if flag:
                err_prob = err_dict
            else:
                probabilities = err_prob
        if isinstance(err_prob, dict):
            for p in Pauli:
                try:
                    probabilities.append(err_prob[p])
                except:
                    probabilities.append(0)
        check_probability(probabilities = probabilities, tolerance = _ATOL)
        self.ideal = False
        if abs(probabilities[0] - 1) < _ATOL:
            self.ideal = True
        self.probabilities = scale_probability(probabilities)
        pass

class DampingError:
    
    '''
    Damping error consists of Amplitude Damping (AD), Generalized Amplitude Damping (GAD), Phase Damping (PD), Generalized Amplitude-Phase Damping (GAPD) and Thermal Relaxation (ThR) errors.
    '''
    
    def __init__(self, type_:str, gamma_am:Optional[Number], gamma_ph:Optional[Number], T1:Optional[Number], T2:Optional[Number], t:Optional[Number], p:Optional[Number], f:Optional[Number], T:Optional[Number]) -> None:
        
        '''
        Create Damping error for noise model
        
        Input:
            Type [str]: Error type from list ['AD', 'GAD', 'PD', 'GAPD', 'ThR']
            gamma_am [float]: Amplitude Damping error parameter (AD, GAD, GAPD)
            gamma_ph [float]: Phase Damping error parameter (PD, GAPD)
            T1 [float]: Energy relaxation time (ThR)
            T2 [float]: Dephasing time (ThR)
            t [float]: Gate time (ThR)
            p [float]: Excited state population (ThR, GAD, GAPD)
            f [float]: Frequency of qubit in GHz (ThR, GAD, GAPD)
            T [float]: Temparature in Kelvin (ThR, GAD, GAPD)
        '''
        
        from math import asin, exp, sqrt
        self.type = type_ + 'Error'
        self.ideal = False
        match type_:
            case 'AD'|'GAD':
            # 'AD' and 'GAD' error
                if not p:
                    if not (f and t):
                        self.probabilities = [0, 1]
                    else:
                        p = 1 / (1 + exp(95.9849 * f / T))
                else:
                    probabilities = [p, 1 - p]
                    check_probability(probabilities = probabilities, tolerance = _ATOL)
                    self.probabilities = scale_probability(probabilities)
                if abs(gamma_am) < _ATOL:
                    self.ideal = True
                if gamma_am < 0:
                    gamma_am = 0
                if gamma_am > 1:
                    gamma_am = 1
                self.gamma_am = gamma_am
                self.theta_am = asin(sqrt(gamma_am))
            case 'PD': pass
            case 'GAPD': pass
            case 'ThR': pass
            case _:
                print(f"Wrong error type: {type_}")
        pass

class ERROR_TYPE(Enum):
    reset = ResetError
    readout = ReadoutError