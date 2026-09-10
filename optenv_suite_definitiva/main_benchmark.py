import argparse
import time
import csv
import os
from mdp_generator import construir_adyacencias, construir_recompensas, construir_politica, elegir_gamma
from transition_finder import encontrar_transicion
from policy_checker import verificar_politica_optima

try:
    from solver_scip import construir_inecuaciones_scip
    SCIP_DISPONIBLE = True
except ImportError:
    SCIP_DISPONIBLE = False

try:
    from solver_gurobi import construir_inecuaciones_gurobi
    GUROBI_DISPONIBLE = True
except ImportError:
    GUROBI_DISPONIBLE = False

def correr_flujo_completo(N, solver_name, writer, archivo_csv):
    print(f"\n{'='*50}")
    print(f" Iniciando pipeline inverso para grilla {N}x{N} ({solver_name.upper()})")
    print(f"{'='*50}")
    
    num_acciones = 5
    gamma = elegir_gamma(0.8, 0.95)
    
    print("[1] Creando MDP (Adyacencias y Recompensas)...")
    adyacencias = construir_adyacencias(N)
    R, r_min, r_max = construir_recompensas(adyacencias)
    pi = construir_politica(N, tipo="random")
    
    limite_min = r_min / (1.0 - gamma)
    limite_max = r_max / (1.0 - gamma)
    
    print(f"[2] Resolviendo inecuaciones Opt-Env con {solver_name.upper()}...")
    inicio = time.time()
    if solver_name == 'gurobi':
        modelo, dict_V = construir_inecuaciones_gurobi(adyacencias, R, pi, num_acciones, gamma, limite_min, limite_max)
    else:
        modelo, dict_V = construir_inecuaciones_scip(adyacencias, R, pi, num_acciones, gamma, limite_min, limite_max)
        
    modelo.optimize()
    tiempo_v = time.time() - inicio
    
    V_optimos = {}
    if solver_name == 'gurobi':
        status_v = "OPTIMAL" if modelo.Status == 2 else "INFEASIBLE"
        vars_totales = modelo.NumVars
        vars_binarias = modelo.NumBinVars
        if modelo.Status == 2:
            V_optimos = {s: var.X for s, var in dict_V.items()}
    else:
        status_v = modelo.getStatus().upper()
        vars_totales = modelo.getNVars()
        vars_binarias = modelo.getNBinVars()
        if modelo.getStatus() == "optimal":
            V_optimos = {s: modelo.getVal(var) for s, var in dict_V.items()}
            
    if not V_optimos:
        print("    -> El solver no encontro un V(s) valido (Infactible). Abortando.")
        writer.writerow([N, solver_name.upper(), round(gamma, 4), vars_totales, vars_binarias, round(tiempo_v, 2), status_v, "", "", "FALLO"])
        archivo_csv.flush()
        return
        
    print(f"    -> V(s) factibles encontrados en {tiempo_v:.2f}s")
    
    print(f"[3] Calculando P(s'|s,a) inversa (LP) a partir de V(s)...")
    inicio = time.time()
    try:
        P_valida = encontrar_transicion(adyacencias, R, V_optimos, pi, num_acciones, gamma, solver_name=solver_name)
        tiempo_p = time.time() - inicio
        status_p = "OPTIMAL"
        print(f"    -> P(s'|s,a) encontrada en {tiempo_p:.2f}s")
    except ValueError as e:
        print(f"    -> Error: {e}")
        writer.writerow([N, solver_name.upper(), round(gamma, 4), vars_totales, vars_binarias, round(tiempo_v, 2), status_v, round(time.time() - inicio, 2), "INFEASIBLE", "FALLO"])
        archivo_csv.flush()
        return
        
    print("[4] Verificando optimalidad estricta de la politica 'Objetivo'...")
    es_optima = verificar_politica_optima(adyacencias, R, P_valida, gamma, pi, num_acciones)
    resultado_final = "EXITOSO" if es_optima else "FALLO"
    print(f"    -> Resultado: {resultado_final}")

    writer.writerow([
        N, solver_name.upper(), round(gamma, 4), vars_totales, vars_binarias, 
        round(tiempo_v, 2), status_v, round(tiempo_p, 2), status_p, resultado_final
    ])
    archivo_csv.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument('--rango', type=int, nargs=2, metavar=('INICIO', 'FIN'))
    grupo.add_argument('--solo', type=int, metavar='N')
    # Nuevo argumento para aceptar listas personalizadas separadas por espacio
    grupo.add_argument('--lista', type=int, nargs='+', metavar='N', help='Lista de tamaños específicos')
    parser.add_argument('--solver', type=str, choices=['scip', 'gurobi'], default='gurobi')
    
    args = parser.parse_args()
    
    if args.solver == 'gurobi' and not GUROBI_DISPONIBLE:
        raise RuntimeError("Gurobi no esta instalado en este entorno virtual.")
    if args.solver == 'scip' and not SCIP_DISPONIBLE:
        raise RuntimeError("PySCIPOpt no esta instalado en este entorno virtual.")
        
    # Lógica de ruteo de tamaños
    if args.rango:
        tamanos = list(range(args.rango[0], args.rango[1] + 1, 5))
    elif args.lista:
        tamanos = args.lista
    else:
        tamanos = [args.solo]
    
    nombre_archivo = "estadisticas_optenv_pi_random.csv"
    archivo_existe = os.path.isfile(nombre_archivo)
    
    with open(nombre_archivo, mode="a", newline="") as archivo_csv:
        writer = csv.writer(archivo_csv)
        if not archivo_existe:
            writer.writerow([
                "N", "Solver", "Gamma", "Variables_Totales", "Variables_Binarias", 
                "Tiempo_Fase_1_MILP_Seg", "Status_Fase_1", 
                "Tiempo_Fase_2_LP_Seg", "Status_Fase_2", "Verificacion_Politica"
            ])
            
        for n in tamanos:
            correr_flujo_completo(n, args.solver, writer, archivo_csv)