from pyscipopt import Model

def construir_inecuaciones_scip(adyacencias, R, pi, num_acciones, gamma, limite_min, limite_max):
    modelo = Model("OptEnv_SCIP")
    modelo.setIntParam("display/verblevel", 0)
    V = {}
    M = limite_max - limite_min
    
    for s in adyacencias:
        V[s] = modelo.addVar(vtype="C", name=f"V_{s[0]}_{s[1]}", lb=limite_min, ub=limite_max)
        
    for s, vecinos in adyacencias.items():
        # Cota Superior (Acción Óptima)
        z_upper = []
        for s_next in vecinos:
            z = modelo.addVar(vtype="B", name=f"z_up_{s[0]}_{s[1]}_{s_next[0]}_{s_next[1]}")
            z_upper.append(z)
            val = R[(s, pi[s], s_next)] + gamma * V[s_next]
            modelo.addCons(V[s] <= val + M * (1 - z))
        modelo.addCons(sum(z_upper) == 1)
        
        # Cota Inferior (Mínimos)
        for a in range(num_acciones):
            y_lower = []
            for s_next in vecinos:
                y = modelo.addVar(vtype="B", name=f"y_low_{s[0]}_{s[1]}_{a}_{s_next[0]}_{s_next[1]}")
                y_lower.append(y)
                val = R[(s, a, s_next)] + gamma * V[s_next]
                
                if a == pi[s]:
                    # La acción óptima puede tocar el piso exacto
                    modelo.addCons(V[s] >= val - M * (1 - y))
                else:
                    # Las subóptimas necesitan holgura para la evaluación estricta en el paso 3
                    modelo.addCons(V[s] >= val + 1e-4 - M * (1 - y))
            modelo.addCons(sum(y_lower) == 1)
            
    modelo.setObjective(0, "maximize")
    return modelo, V