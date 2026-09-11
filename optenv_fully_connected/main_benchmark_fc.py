import argparse
import time
import csv
import os
from mdp_generator_fc import construir_adyacencias, construir_recompensas, construir_politica, elegir_gamma
from transition_finder_fc import encontrar_transicion
from policy_checker_fc import verificar_politica_optima
from solver_gurobi_fc import construir_inecuaciones_gurobi

def correr_flujo_completo(N, writer, archivo_csv):
    print(f"\n{'='*50}")
    print(f" Iniciando pipeline inverso para Grafo Completo ({N} nodos)")
    print(f"{'='*50}")
    
    num_acciones = 5
    gamma = elegir_gamma(0.8, 0.95)
    
    print("[1] Creando MDP (Adyacencias Completas y Recompensas)...")
    adyacencias = construir_adyacencias(N)
    R, r_min, r_max = construir_recompensas(adyacencias, num_acciones=num_acciones)
    pi = construir_politica(N, num_acciones=num_acciones)
    
    limite_min = r_min / (1.0 - gamma)
    limite_max = r_max / (1.0 - gamma)
    
    print("[2] Resolviendo inecuaciones Opt-Env con GUROBI...")
    inicio = time.time()
    modelo, dict_V = construir_inecuaciones_gurobi(adyacencias, R, pi, num_acciones, gamma, limite_min, limite_max)
    modelo.optimize()
    tiempo_v = time.time() - inicio
    
    status_v = "OPTIMAL" if modelo.Status == 2 else "INFEASIBLE"
    vars_totales = modelo.NumVars
    vars_binarias = modelo.NumBinVars
    
    if modelo.Status != 2:
        print("    -> El solver no encontro un V(s) valido (Infactible). Abortando.")
        writer.writerow([N, round(gamma, 4), vars_totales, vars_binarias, round(tiempo_v, 2), status_v, "", "", "FALLO"])
        archivo_csv.flush()
        return
        
    V_optimos = {s: var.X for s, var in dict_V.items()}
    print(f"    -> V(s) factibles encontrados en {tiempo_v:.2f}s")
    
    print("[3] Calculando P(s'|s,a) inversa (LP) a partir de V(s)...")
    inicio = time.time()
    try:
        P_valida = encontrar_transicion(adyacencias, R, V_optimos, pi, num_acciones, gamma)
        tiempo_p = time.time() - inicio
        status_p = "OPTIMAL"
        print(f"    -> P(s'|s,a) encontrada en {tiempo_p:.2f}s")
    except ValueError as e:
        print(f"    -> Error: {e}")
        writer.writerow([N, round(gamma, 4), vars_totales, vars_binarias, round(tiempo_v, 2), status_v, round(time.time() - inicio, 2), "INFEASIBLE", "FALLO"])
        archivo_csv.flush()
        return
        
    print("[4] Verificando optimalidad estricta de la politica Random...")
    es_optima = verificar_politica_optima(adyacencias, R, P_valida, gamma, pi, num_acciones)
    resultado_final = "EXITOSO" if es_optima else "FALLO"
    print(f"    -> Resultado: {resultado_final}")

    writer.writerow([
        N, round(gamma, 4), vars_totales, vars_binarias, 
        round(tiempo_v, 2), status_v, round(tiempo_p, 2), status_p, resultado_final
    ])
    archivo_csv.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument('--rango', type=int, nargs=2, metavar=('INICIO', 'FIN'))
    grupo.add_argument('--solo', type=int, metavar='N')
    grupo.add_argument('--lista', type=int, nargs='+', metavar='N', help='Lista de tamaños')
    
    args = parser.parse_args()
    
    if args.rango:
        tamanos = list(range(args.rango[0], args.rango[1] + 1, 5))
    elif args.lista:
        tamanos = args.lista
    else:
        tamanos = [args.solo]
    
    nombre_archivo = "estadisticas_optenv_fc.csv"
    archivo_existe = os.path.isfile(nombre_archivo)
    
    with open(nombre_archivo, mode="a", newline="") as archivo_csv:
        writer = csv.writer(archivo_csv)
        if not archivo_existe:
            writer.writerow([
                "N_Nodos", "Gamma", "Variables_Totales", "Variables_Binarias", 
                "Tiempo_Fase_1_MILP_Seg", "Status_Fase_1", 
                "Tiempo_Fase_2_LP_Seg", "Status_Fase_2", "Verificacion_Politica"
            ])
            
        for n in tamanos:
            correr_flujo_completo(n, writer, archivo_csv)
