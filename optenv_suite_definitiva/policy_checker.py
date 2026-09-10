import numpy as np

def verificar_politica_optima(adyacencias, R, P, gamma, pi, num_acciones):
    estados = list(adyacencias.keys())
    N_estados = len(estados)
    s_to_idx = {s: i for i, s in enumerate(estados)}
    
    P_pi = np.zeros((N_estados, N_estados))
    R_pi = np.zeros(N_estados)
    
    for s in estados:
        i = s_to_idx[s]
        a = pi[s]
        vecinos = adyacencias[s]
        
        R_pi[i] = sum(P[(s, a, s_next)] * R[(s, a, s_next)] for s_next in vecinos)
        for s_next in vecinos:
            j = s_to_idx[s_next]
            P_pi[i, j] = P[(s, a, s_next)]
            
    # Resolvemos el sistema: V_pi = R_pi + gamma * P_pi * V_pi
    I = np.eye(N_estados)
    V_pi_array = np.linalg.solve(I - gamma * P_pi, R_pi)
    V_pi = {s: V_pi_array[s_to_idx[s]] for s in estados}
    
    es_optima = True
    for s in estados:
        vecinos = adyacencias[s]
        for a in range(num_acciones):
            q_a = sum(P[(s, a, s_next)] * (R[(s, a, s_next)] + gamma * V_pi[s_next]) for s_next in vecinos)
            
            # Condicion Opt-Env: V(s) >= Q(s,a) para toda accion
            if q_a > V_pi[s] + 1e-5:
                es_optima = False
                break
        if not es_optima:
            break
            
    return es_optima
