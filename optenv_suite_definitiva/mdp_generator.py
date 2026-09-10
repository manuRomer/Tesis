import random

def construir_adyacencias(N):
    # Vecindad ortogonal (L1) segun la definicion de la tesis
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
    return adyacencias

def construir_recompensas(adyacencias, cota_min=-10, cota_max=10, num_acciones=5):
    R = {}
    for s, destinos in adyacencias.items():
        for a in range(num_acciones):
            for s_prime in destinos:
                R[(s, a, s_prime)] = random.uniform(cota_min, cota_max)
    return R, cota_min, cota_max

def construir_politica(N, tipo="objetivo", accion_constante=0, esquina_objetivo=(0, 0)):
    pi = {}
    for x in range(N):
        for y in range(N):
            s = (x, y)
            if tipo == "constante":
                pi[s] = accion_constante
            elif tipo == "random":
                pi[s] = random.randint(0, 4)
            elif tipo == "objetivo":
                tx, ty = esquina_objetivo
                if x < tx: pi[s] = 1
                elif x > tx: pi[s] = 2
                elif y < ty: pi[s] = 3
                elif y > ty: pi[s] = 4
                else: pi[s] = 0
    return pi

def elegir_gamma(min_val=0.5, max_val=0.99):
    return random.uniform(min_val, max_val)
