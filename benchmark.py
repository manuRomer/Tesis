import time
import csv
from mdp import construir_adyacencias, construir_recompensas, construir_politica, elegir_gamma
from gurobi import construir_modelo_gurobi

if __name__ == "__main__":
    # Arrancamos con grillas chicas para no saturar la Mac en las primeras pruebas
    tamanos_grilla = [5, 10, 15] 
    num_acciones = 5
    
    # Abrimos el CSV en modo escritura
    with open("resultados_benchmark.csv", mode="w", newline="") as archivo_csv:
        writer = csv.writer(archivo_csv)
        # Encabezados para la tesis
        writer.writerow(["N", "Gamma", "Variables_Binarias", "Tiempo_Segundos", "Status"])
        
        for N in tamanos_grilla:
            print(f"\n--- Evaluando grilla {N}x{N} ---")
            
            # 1. Generar MDP
            adyacencias = construir_adyacencias(N)
            R, r_min, r_max = construir_recompensas(adyacencias, num_acciones=num_acciones)
            pi = construir_politica(N, tipo="objetivo", esquina_objetivo=(N-1, N-1))
            gamma = elegir_gamma(0.8, 0.95)
            
            # 2. Calcular límites teóricos exactos
            limite_min_v = r_min / (1.0 - gamma)
            limite_max_v = r_max / (1.0 - gamma)
            
            # 3. Construir modelo
            print("Construyendo inecuaciones de Bellman...")
            modelo, V = construir_modelo_gurobi(
                adyacencias, R, pi, num_acciones, gamma, limite_min_v, limite_max_v
            )
            
            # Configuraciones del solver
            modelo.setParam('OutputFlag', 1)  # 1 para ver el log de Gurobi, 0 para silenciarlo
            modelo.setParam('TimeLimit', 300) # Cortar a los 5 minutos si se traba
            
            # 4. Resolver
            print("Ejecutando solver...")
            inicio = time.time()
            modelo.optimize()
            fin = time.time()
            
            tiempo_total = fin - inicio
            estado = modelo.Status
            vars_binarias = modelo.NumBinVars
            
            print(f"Status: {estado} | Tiempo: {tiempo_total:.2f}s | Vars Binarias inyectadas: {vars_binarias}")
            
            # Guardar la fila en el CSV
            writer.writerow([N, gamma, vars_binarias, round(tiempo_total, 2), estado])
            
    print("\n¡Benchmark terminado! Revisá el archivo resultados_benchmark.csv")