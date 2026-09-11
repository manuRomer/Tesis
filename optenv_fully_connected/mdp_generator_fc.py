import random

def construir_adyacencias(N):
    # Grafo completamente conectado: todos los nodos van a todos los nodos (0 a N-1)
    return {s: list(range(N)) for s in range(N)}

def construir_recompensas(adyacencias, cota_min=-10, cota_max=10, num_acciones=5):
    R = {}
    for s, destinos in adyacencias.items():
        for a in range(num_acciones):
            for s_prime in destinos:
                R[(s, a, s_prime)] = random.uniform(cota_min, cota_max)
    return R, cota_min, cota_max

def construir_politica(N, num_acciones=5):
    # Asignacion aleatoria estricta por nodo
    return {s: random.randint(0, num_acciones - 1) for s in range(N)}

def elegir_gamma(min_val=0.5, max_val=0.99):
    return random.uniform(min_val, max_val)
