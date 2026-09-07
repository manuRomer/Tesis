import gurobipy as gp
from gurobipy import GRB

def construir_modelo_gurobi(adyacencias, R, pi, num_acciones, gamma, limite_min_v, limite_max_v):
    # Inicializamos el entorno matemático
    modelo = gp.Model("Opt-Env-Gridworld")
    
    # 1. Variables de Decisión Principales: V(s)
    # Usamos tupledict para mapear V[(x,y)] y acotamos con limite_v para ayudar al solver
    V = {}
    for s in adyacencias.keys():
        V[s] = modelo.addVar(lb=limite_min_v, ub=limite_max_v, name=f"V_{s}")
        
    # Actualizamos el modelo para que las variables existan en memoria antes de usarlas
    modelo.update()

    # 2. Inyección de Restricciones
    for s, vecinos in adyacencias.items():
        
        # --- COTA SUPERIOR: V(s) <= max_{s'} [ R(s, pi(s), s') + gamma * V(s') ] ---
        accion_optima = pi[s]
        aux_destinos_max = []
        
        for s_prime in vecinos:
            # Gurobi exige una variable auxiliar por cada cálculo interno del max()
            aux_val = modelo.addVar(lb=limite_min_v, ub=limite_max_v, name=f"aux_max_{s}_{s_prime}")
            recompensa = R[(s, accion_optima, s_prime)]
            modelo.addConstr(aux_val == recompensa + gamma * V[s_prime])
            aux_destinos_max.append(aux_val)
            
        # Variable que representará el resultado del max()
        max_s = modelo.addVar(lb=limite_min_v, ub=limite_max_v, name=f"max_{s}")
        modelo.addConstr(max_s == gp.max_(aux_destinos_max))
        
        # Restricción final de la cota superior
        modelo.addConstr(V[s] <= max_s, name=f"CotaSup_{s}")
        
        
        # --- COTA INFERIOR: V(s) >= min_{s'} [ R(s, a, s') + gamma * V(s') ] para todo a ---
        for a in range(num_acciones):
            aux_destinos_min = []
            
            for s_prime in vecinos:
                aux_val = modelo.addVar(lb=limite_min_v, ub=limite_max_v, name=f"aux_min_{s}_{a}_{s_prime}")
                recompensa = R[(s, a, s_prime)]
                modelo.addConstr(aux_val == recompensa + gamma * V[s_prime])
                aux_destinos_min.append(aux_val)
                
            # Variable que representará el resultado del min()
            min_s_a = modelo.addVar(lb=limite_min_v, ub=limite_max_v, name=f"min_{s}_{a}")
            modelo.addConstr(min_s_a == gp.min_(aux_destinos_min))
            
            # Restricción final de la cota inferior
            modelo.addConstr(V[s] >= min_s_a, name=f"CotaInf_{s}_{a}")

    return modelo, V