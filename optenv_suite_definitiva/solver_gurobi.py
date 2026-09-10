import gurobipy as gp
from gurobipy import GRB

def construir_inecuaciones_gurobi(adyacencias, R, pi, num_acciones, gamma, limite_min, limite_max):
    modelo = gp.Model("OptEnv_Gurobi")
    modelo.setParam('OutputFlag', 0)
    V = {}
    M = limite_max - limite_min
    
    for s in adyacencias:
        V[s] = modelo.addVar(vtype=GRB.CONTINUOUS, lb=limite_min, ub=limite_max, name=f"V_{s[0]}_{s[1]}")
        
    for s, vecinos in adyacencias.items():
        # Cota Superior
        z_upper = []
        for s_next in vecinos:
            z = modelo.addVar(vtype=GRB.BINARY, name=f"z_up_{s[0]}_{s[1]}_{s_next[0]}_{s_next[1]}")
            z_upper.append(z)
            val = R[(s, pi[s], s_next)] + gamma * V[s_next]
            modelo.addConstr(V[s] <= val + M * (1 - z))
        modelo.addConstr(gp.quicksum(z_upper) == 1)
        
        # Cota Inferior
        for a in range(num_acciones):
            y_lower = []
            for s_next in vecinos:
                y = modelo.addVar(vtype=GRB.BINARY, name=f"y_low_{s[0]}_{s[1]}_{a}_{s_next[0]}_{s_next[1]}")
                y_lower.append(y)
                val = R[(s, a, s_next)] + gamma * V[s_next]
                
                if a == pi[s]:
                    modelo.addConstr(V[s] >= val - M * (1 - y))
                else:
                    modelo.addConstr(V[s] >= val + 1e-4 - M * (1 - y))
            modelo.addConstr(gp.quicksum(y_lower) == 1)
            
    modelo.setObjective(0, GRB.MAXIMIZE)
    return modelo, V