import gurobipy as gp
from gurobipy import GRB

def encontrar_transicion(adyacencias, R, V_optimos, pi, num_acciones, gamma):
    modelo = gp.Model("Transition_Finder_Gurobi_FC")
    modelo.setParam('OutputFlag', 0)
    
    P = {}
    for s, vecinos in adyacencias.items():
        for a in range(num_acciones):
            for s_next in vecinos:
                P[(s, a, s_next)] = modelo.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name=f"P_{s}_{a}_{s_next}")
                
    for s, vecinos in adyacencias.items():
        for a in range(num_acciones):
            # Suma = 1 iterando sobre TODOS los nodos N
            modelo.addConstr(gp.quicksum(P[(s, a, s_next)] for s_next in vecinos) == 1.0)
            
            esperanza = gp.quicksum(P[(s, a, s_next)] * (R[(s, a, s_next)] + gamma * V_optimos[s_next]) for s_next in vecinos)
            
            if a == pi[s]:
                modelo.addConstr(esperanza == V_optimos[s])
            else:
                modelo.addConstr(V_optimos[s] >= esperanza + 1e-4)
                
    modelo.setObjective(0, GRB.MINIMIZE)
    modelo.optimize()
    
    if modelo.Status != 2:
        raise ValueError("Infactible: Los valores V(s) no permiten construir una transicion valida.")
        
    return {key: var.X for key, var in P.items()}
