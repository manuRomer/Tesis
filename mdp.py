# Primero vamos a escribir la logica de generacion de MDPs.
# El grafo es un diccionario indexado por la la tupla (x, y).
# La reward function es un diccionario indexado por la tupla (estado_origen, accion, estado_destino).
# La policy puede ser de 3 tipos: 
#       constante: siempre la misma accion
#       objetivo: intenta llegar a una esquina especifica
#       random: se elige una accion random para cada estado


import random

def construir_adyacencias(N):
    # (0, 0): quedarse en el lugar; desplazamientos en cruz para la vecindad ortogonal
    offsets = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    adyacencias = {}

    for x in range(N):
        for y in range(N):
            vecinos = []
            for dx, dy in offsets:
                nx, ny = x + dx, y + dy
                if 0 <= nx < N and 0 <= ny < N:
                    vecinos.append((nx, ny))
            adyacencias[(x, y)] = vecinos
    # Conexiones válidas en el grafo es 5N^2 - 4N   
    return adyacencias

def construir_recompensas(adyacencias, cota_min_reward=-10, cota_max_reward=10, num_acciones=5):
    R = {}
    
    # Iteramos solo sobre las posiciones válidas del Gridworld
    for s, destinos_validos in adyacencias.items():
        for a in range(num_acciones):
            for s_prime in destinos_validos:
                # s y s_prime son tuplas (x, y)
                # Asignamos una recompensa simulada entre -10 y 10
                R[(s, a, s_prime)] = random.uniform(cota_min_reward, cota_max_reward)
                
    return R, cota_min_reward, cota_max_reward

import random

def construir_politica(N, tipo="constante", accion_constante=0, esquina_objetivo=(0, 0)):
    """
    Mapeo de las 5 acciones (asumiendo offsets cartesianos):
    0: Quedarse  (0, 0)
    1: Derecha   (1, 0)
    2: Izquierda (-1, 0)
    3: Arriba    (0, 1)
    4: Abajo     (0, -1)
    """
    pi = {}
    
    for x in range(N):
        for y in range(N):
            s = (x, y)
            
            if tipo == "constante":
                # Asigna siempre la misma acción
                pi[s] = accion_constante
                
            elif tipo == "random":
                # Asigna una acción aleatoria entre 0 y 4
                pi[s] = random.randint(0, 4)
                
            elif tipo == "objetivo":
                tx, ty = esquina_objetivo
                
                # Lógica greedy para reducir la distancia Manhattan hacia el objetivo
                if x < tx:
                    pi[s] = 1  # Mover a la derecha
                elif x > tx:
                    pi[s] = 2  # Mover a la izquierda
                elif y < ty:
                    pi[s] = 3  # Mover hacia arriba
                elif y > ty:
                    pi[s] = 4  # Mover hacia abajo
                else:
                    pi[s] = 0  # Quedarse (ya está en la esquina objetivo)
                    
    return pi

def elegir_gamma(min_val=0.5, max_val=0.99):
    """
    Selecciona aleatoriamente un factor de descuento gamma dentro del rango [min_val, max_val].
    """
    # Validación matemática para asegurar que gamma no sea menor a 0 ni igual a 1
    min_val = max(0.0, min_val)
    max_val = min(0.9999, max_val)
    
    if min_val >= max_val:
        raise ValueError("min_val debe ser estrictamente menor que max_val")
        
    gamma = random.uniform(min_val, max_val)
    
    return gamma