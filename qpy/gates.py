from typing import Iterable

import numpy as np

# Utility: Perform calculations successively on operator matrices
def kron(operators: Iterable[np.ndarray]) -> np.ndarray:
    '''
    Successive kronecker function for multiple operators
    `kron([A, B, C])` => `np.kron(np.kron(A, B), C)`
    '''
    result = operators[0]
    for op in operators[1:]:
        result = np.kron(result, op)
    return result

def dot(operators: Iterable[np.ndarray]) -> np.ndarray:
    '''
    Successive dot product for multiple operators
    `dot([A, B, C])` => `np.dot(np.dot(A, B), C)`
    '''
    result = operators[0]
    for op in operators[1:]:
        result = np.dot(result, op)
    return result



# Utility: Add gate logic
def add_gate(gate:np.ndarray, targetq:int, num_qubits:int) -> np.ndarray:
    start_pad = targetq
    end_pad = num_qubits - (targetq + 1)
    
    operator = kron([I]*start_pad + [gate] + [I]*end_pad)
    
    return operator

def control_gate(gate: np.ndarray, control_qubit: int, target_qubit: int, num_qubits: int):
    
    if control_qubit == target_qubit:
        raise ValueError("Control and Target qubits must be different.")
    
    if not (0 <= control_qubit <= num_qubits) or not (0 <= target_qubit <= num_qubits):
        raise ValueError("Error")
        

    # Apply the controlled gate with padding
    if control_qubit < target_qubit:
        operator = add_gate(np.outer(zero,zero), control_qubit, num_qubits) + kron([*[I]*(control_qubit), np.outer(one,one), *[I]*(target_qubit - control_qubit - 1), gate, *[I]*(num_qubits - target_qubit - 1)])
    else: 
        operator = add_gate(np.outer(zero,zero), control_qubit, num_qubits) + kron([*[I]*(target_qubit), gate, *[I]*(control_qubit - target_qubit - 1), np.outer(one,one), *[I]*(num_qubits - control_qubit - 1)])
        
    return operator



zero = np.array([1,0])
one = np.array([0,1])
plus = 1/np.sqrt(2) * np.array([1,1])
I = np.eye(2)

#Single Qubit Operations
#Pauli-X
X = np.array([[0,1], 
              [1,0]])

#Paui-Y
Y = np.array([[0,-1j],
              [1j,0]])

#Pauli-Z 
Z = np.array([[1,0],
              [0,-1]])

#Hadamard
H = 1/np.sqrt(2)*np.array([[1,1],
                           [1,-1]])

#Phase (S,P)
S = np.array([[1,0],
              [0,1j]])

#pi/8
T = np.array([[1,0],
              [0,np.exp(1j*np.pi/4)]])

#Controlled Not / CX
cnot = np.array([[1,0,0,0],
                 [0,1,0,0],
                 [0,0,0,1],
                 [0,0,1,0]])

#Controlled Z
CZ = np.array([[1,0,0,0],
               [0,1,0,0],
               [0,0,1,0],
               [0,0,0,-1]])

swap = np.array([[1,0,0,0],
                 [0,0,1,0],
                 [0,1,0,0],
                 [0,0,0,1]])


def Rx(theta):
    return np.array([[np.cos(theta/2), -1j*np.sin(theta/2)],
                    [-1j*np.sin(theta/2), np.cos(theta/2)]])

def Rz(theta):
    return np.array([[1,0],[0, np.exp(1j*theta)]])



# implement CNOT on adjacent qubits
def cnot_adj(controlq, targetq, num_qubits):
    if targetq != controlq + 1:
        raise ValueError("Control and Target qubits must be adjacent.")
    
    #pad CNOT matrix 
    start_padding = controlq
    end_padding = num_qubits - (targetq + 1)
    operator = kron([*[I]*start_padding, cnot, *[I]*end_padding])

    return operator


#implementing CNOT on non-adjacent qubits 
def cnot_nonadj(control_qubit:int, target_qubit:int, num_qubits:int) -> np.ndarray:
    
    if control_qubit == target_qubit:
        raise ValueError("Control and Target qubits must be different.")
    
    if not (0<= control_qubit <= num_qubits) or not (0<= target_qubit <= num_qubits):
        raise ValueError("Error")
        

    # Apply the controlled NOT gate with padding
    if control_qubit < target_qubit:
        operator = kron([*[I]*(control_qubit), np.outer(zero,zero), *[I]*(num_qubits - control_qubit - 1)]) + kron([*[I]*(control_qubit), np.outer(one,one), *[I]*(target_qubit - control_qubit - 1), X, *[I]*(num_qubits - target_qubit - 1)])
    else: 
        operator = kron([*[I]*(control_qubit), np.outer(zero,zero), *[I]*(num_qubits - control_qubit - 1)]) + kron([*[I]*(target_qubit), X, *[I]*(control_qubit - target_qubit - 1), np.outer(one,one), *[I]*(num_qubits - control_qubit - 1)])
        
    return operator


# function to generate a GHZ State
def generate_ghz_state(num_qubits):
    # Initialising the state to |0...0⟩
    ghz_state = kron([zero] * (num_qubits))

    # Apply Hadamard gate to the last qubit
    ghz_state = add_gate(H,0,num_qubits)@ghz_state

    # Apply CNOT gates to create GHZ state
    for i in range(num_qubits - 1):
        ghz_state = cnot_adj(i, i+1, num_qubits)@ghz_state
            
    return ghz_state



#toffoli gate 
def TOFFOLI(control1, control2, target, num_qubits):
    
    if control1 == target or control2 == target:
        raise ValueError("Control and Target qubits must be different.")
    
    if not (0<= control1 <= num_qubits-1) or not (0<= target <= num_qubits-1) or not (0<= control2 <= num_qubits-1):
        raise ValueError("Control and target qubits must be within range")
        
    # Ensure control_qubits are ordered in ascending order of indices
    c1, c2 = sorted([control1, control2])

    # Apply the controlled NOT gate with padding
    if c2 < target:     
        term1 = kron([*[I]*(c1), np.outer(zero,zero), *[I]*(c2 - c1 - 1), np.outer(zero,zero), *[I]*(target - c2 - 1), I, *[I]*(num_qubits - target - 1)])
        term2 = kron([*[I]*(c1), np.outer(one,one), *[I]*(c2 - c1 - 1), np.outer(zero,zero), *[I]*(target - c2 - 1), I, *[I]*(num_qubits - target - 1)]) 
        term3 = kron([*[I]*(c1), np.outer(zero,zero), *[I]*(c2 - c1 - 1), np.outer(one,one), *[I]*(target - c2 - 1), I, *[I]*(num_qubits - target - 1)]) 
        term4 = kron([*[I]*(c1), np.outer(one,one), *[I]*(c2 - c1 - 1), np.outer(one,one), *[I]*(target - c2 - 1), X, *[I]*(num_qubits - target - 1)])
        operator = term1 + term2 + term3 + term4
        
    elif c1 < target < c2: # If target qubit is in the middle of both controls
        term1 = kron([*[I]*(c1), np.outer(zero,zero), *[I]*(target - c1 - 1), I, *[I]*(c2 - target - 1), np.outer(zero,zero), *[I]*(num_qubits - c2 - 1)]) 
        term2 = kron([*[I]*(c1), np.outer(one,one), *[I]*(target - c1 - 1), I, *[I]*(c2 - target - 1), np.outer(zero,zero), *[I]*(num_qubits - c2 - 1)]) 
        term3 = kron([*[I]*(c1), np.outer(zero,zero), *[I]*(target - c1 - 1), I, *[I]*(c2 - target - 1), np.outer(one,one), *[I]*(num_qubits - c2 - 1)]) 
        term4 = kron([*[I]*(c1), np.outer(one,one), *[I]*(target - c1 - 1), X, *[I]*(c2 - target - 1), np.outer(one,one), *[I]*(num_qubits - c2 - 1)])
        operator = term1 + term2 + term3 + term4
        
    elif target < c1: # if target is before both controls
        term1 = kron([*[I]*(target), I, *[I]*(c1 - target - 1), np.outer(zero,zero), *[I]*(c2 - c1- 1), np.outer(zero,zero), *[I]*(num_qubits - c2 - 1)])
        term2 = kron([*[I]*(target), I, *[I]*(c1 - target - 1), np.outer(one,one), *[I]*(c2 - c1- 1), np.outer(zero,zero), *[I]*(num_qubits - c2 - 1)])
        term3 = kron([*[I]*(target), I, *[I]*(c1 - target - 1), np.outer(zero,zero), *[I]*(c2 - c1- 1), np.outer(one,one), *[I]*(num_qubits - c2 - 1)])
        term4 = kron([*[I]*(target), X, *[I]*(c1 - target - 1), np.outer(one,one), *[I]*(c2 - c1- 1), np.outer(one, one), *[I]*(num_qubits - c2 - 1)])
        operator = term1 + term2 + term3 + term4
        
    return operator
    