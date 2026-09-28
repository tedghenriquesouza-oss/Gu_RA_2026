def controle_reativo(distancias):
    """
    Controle reativo de obstáculos.

    Parâmetros:
        distancias: dicionário contendo:
            'frente'
            'esquerda'
            'direita'

    Retorna:
        v: velocidade linear (m/s)
        omega: velocidade angular (rad/s)
    """

    # Distâncias dos sensores
    frente = distancias['frente']
    esquerda = distancias['esquerda']
    direita = distancias['direita']

    # Distância crítica para acionar o freio
    distancia_critica = 0.4

    # =====================================================
    # SITUAÇÃO 1: OBSTÁCULO MUITO PRÓXIMO
    # =====================================================

    if frente < distancia_critica:

        # Freia o robô
        v = 0.0

        # Gira para o lado que estiver mais livre
        if esquerda > direita:
            omega = 1.0
        else:
            omega = -1.0

    # =====================================================
    # SITUAÇÃO 2: FRENTE LIVRE
    # =====================================================

    else:

        # Avança
        v = 0.5

        # Controle proporcional:
        # se esquerda > direita, gira para a esquerda
        # se direita > esquerda, gira para a direita
        ganho = 1.0

        omega = ganho * (esquerda - direita)

    return v, omega


# =====================================================
# TESTES
# =====================================================

# Teste 1: obstáculo na frente
distancias_1 = {
    'frente': 0.3,
    'esquerda': 2.0,
    'direita': 0.8
}

v, omega = controle_reativo(distancias_1)

print("Teste 1:")
print(f"v = {v:.2f} m/s")
print(f"omega = {omega:.2f} rad/s")


# Teste 2: frente livre, esquerda mais livre
distancias_2 = {
    'frente': 2.0,
    'esquerda': 3.0,
    'direita': 1.5
}

v, omega = controle_reativo(distancias_2)

print("\nTeste 2:")
print(f"v = {v:.2f} m/s")
print(f"omega = {omega:.2f} rad/s")


# Teste 3: frente livre, direita mais livre
distancias_3 = {
    'frente': 2.0,
    'esquerda': 1.0,
    'direita': 3.0
}

v, omega = controle_reativo(distancias_3)

print("\nTeste 3:")
print(f"v = {v:.2f} m/s")
print(f"omega = {omega:.2f} rad/s")
