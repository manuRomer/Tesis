from pyscipopt import Model

def encontrar_transicion(adyacencias, R, V_optimos, pi, num_acciones, gamma):
    modelo = Model("Transition_Finder_Policy")
    modelo.setIntParam("display/verblevel", 0)
    
    P = {}
    for s, vecinos in adyacencias.items():
        for a in range(num_acciones):
            for s_next in vecinos:
                P[(s, a, s_next)] = modelo.addVar(vtype="C", lb=0.0, ub=1.0, name=f"P_{s}_{a}_{s_next}")
                
    for s, vecinos in adyacencias.items():
        for a in range(num_acciones):
            # Axioma de probabilidad dentro de la vecindad
            modelo.addCons(sum(P[(s, a, s_next)] for s_next in vecinos) == 1.0)
            
            # Valor esperado Q(s,a)
            esperanza = sum(P[(s, a, s_next)] * (R[(s, a, s_next)] + gamma * V_optimos[s_next]) for s_next in vecinos)
            
            if a == pi[s]:
                # La accion optima debe igualar estrictamente a V(s)
                modelo.addCons(esperanza == V_optimos[s])
            else:
                # Las acciones suboptimas deben ser menores (V(s) >= Q(s,a))
                # Se suma 1e-4 para forzar optimalidad estricta
                modelo.addCons(V_optimos[s] >= esperanza + 1e-4)
                
    modelo.setObjective(0, "minimize")
    modelo.optimize()
    
    if modelo.getStatus() != "optimal":
        raise ValueError("Infactible: Los valores V(s) no permiten construir una transicion valida.")
        
    P_final = {}
    for key, var in P.items():
        P_final[key] = modelo.getVal(var)
        
    return P_final
