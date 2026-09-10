def encontrar_transicion(adyacencias, R, V_optimos, pi, num_acciones, gamma, solver_name="gurobi"):
    if solver_name == "gurobi":
        import gurobipy as gp
        from gurobipy import GRB
        
        modelo = gp.Model("Transition_Finder_Gurobi")
        modelo.setParam('OutputFlag', 0)
        
        P = {}
        for s, vecinos in adyacencias.items():
            for a in range(num_acciones):
                for s_next in vecinos:
                    P[(s, a, s_next)] = modelo.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name=f"P_{s}_{a}_{s_next}")
                    
        for s, vecinos in adyacencias.items():
            for a in range(num_acciones):
                # Suma de probabilidades = 1
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
        
    else:
        from pyscipopt import Model
        modelo = Model("Transition_Finder_SCIP")
        modelo.setIntParam("display/verblevel", 0)
        
        P = {}
        for s, vecinos in adyacencias.items():
            for a in range(num_acciones):
                for s_next in vecinos:
                    P[(s, a, s_next)] = modelo.addVar(vtype="C", lb=0.0, ub=1.0, name=f"P_{s}_{a}_{s_next}")
                    
        for s, vecinos in adyacencias.items():
            for a in range(num_acciones):
                modelo.addCons(sum(P[(s, a, s_next)] for s_next in vecinos) == 1.0)
                esperanza = sum(P[(s, a, s_next)] * (R[(s, a, s_next)] + gamma * V_optimos[s_next]) for s_next in vecinos)
                
                if a == pi[s]:
                    modelo.addCons(esperanza == V_optimos[s])
                else:
                    modelo.addCons(V_optimos[s] >= esperanza + 1e-4)
                    
        modelo.setObjective(0, "minimize")
        modelo.optimize()
        
        if modelo.getStatus() != "optimal":
            raise ValueError("Infactible: Los valores V(s) no permiten construir una transicion valida.")
            
        return {key: modelo.getVal(var) for key, var in P.items()}