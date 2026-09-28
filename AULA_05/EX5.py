import math


def calcular_orientacao_alvo(x, y, theta, x_alvo, y_alvo, Kp=1.5):
    """
    Calcula a velocidade angular para apontar o robô para o alvo.
    """

    # Ângulo desejado até o alvo
    theta_alvo = math.atan2(
        y_alvo - y,
        x_alvo - x
    )

    # Erro angular
    e_theta = theta_alvo - theta

    # Normaliza o erro para [-pi, pi]
    while e_theta > math.pi:
        e_theta -= 2 * math.pi

    while e_theta < -math.pi:
        e_theta += 2 * math.pi

    # Controle proporcional
    omega = Kp * e_theta

    return omega


def controle_reativo(distancias):
    """
    Controle de desvio de obstáculos.
    """

    frente = distancias['frente']
    esquerda = distancias['esquerda']
    direita = distancias['direita']

    # Obstáculo muito próximo
    if frente < 0.4:

        v = 0.0

        # Gira para o lado mais livre
        if esquerda > direita:
            omega = 1.0
        else:
            omega = -1.0

    else:

        # Frente livre
        v = 0.5

        # Controle proporcional
        ganho = 1.0
        omega = ganho * (esquerda - direita)

    return v, omega


def maquina_de_estados(
    x, y, theta,
    x_alvo, y_alvo,
    dist_frente, dist_esq, dist_dir
):
    """
    Máquina de Estados Finitos do robô.

    Estados:
        IR_PARA_ALVO
        DESVIAR_OBSTACULO
        OBJETIVO_ALCANÇADO

    Retorna:
        estado_atual, v_cmd, omega_cmd
    """

    # =====================================================
    # 1. CALCULA A DISTÂNCIA ATÉ O ALVO
    # =====================================================

    distancia_alvo = math.sqrt(
        (x_alvo - x) ** 2 +
        (y_alvo - y) ** 2
    )

    # =====================================================
    # 2. VERIFICA SE O OBJETIVO FOI ALCANÇADO
    # =====================================================

    if distancia_alvo < 0.2:

        estado_atual = "OBJETIVO_ALCANÇADO"

        # Robô parado
        v_cmd = 0.0
        omega_cmd = 0.0

    # =====================================================
    # 3. VERIFICA OBSTÁCULO
    # =====================================================

    elif dist_frente < 0.5:

        estado_atual = "DESVIAR_OBSTACULO"

        # Usa a lógica do Exercício 3
        distancias = {
            'frente': dist_frente,
            'esquerda': dist_esq,
            'direita': dist_dir
        }

        v_cmd, omega_cmd = controle_reativo(distancias)

    # =====================================================
    # 4. CAMINHO LIVRE: IR PARA O ALVO
    # =====================================================

    else:

        estado_atual = "IR_PARA_ALVO"

        # Velocidade linear
        v_cmd = 0.5

        # Usa a lógica do Exercício 4
        omega_cmd = calcular_orientacao_alvo(
            x,
            y,
            theta,
            x_alvo,
            y_alvo
        )

    return estado_atual, v_cmd, omega_cmd


# =====================================================
# TESTES
# =====================================================

# -----------------------------------------------------
# TESTE 1: Robô está longe do alvo e sem obstáculo
# -----------------------------------------------------

resultado = maquina_de_estados(
    x=0.0,
    y=0.0,
    theta=0.0,
    x_alvo=2.0,
    y_alvo=2.0,
    dist_frente=2.0,
    dist_esq=2.0,
    dist_dir=2.0
)

print("TESTE 1")
print(f"Estado: {resultado[0]}")
print(f"v = {resultado[1]:.2f} m/s")
print(f"omega = {resultado[2]:.2f} rad/s")


# -----------------------------------------------------
# TESTE 2: Existe obstáculo na frente
# -----------------------------------------------------

resultado = maquina_de_estados(
    x=0.0,
    y=0.0,
    theta=0.0,
    x_alvo=2.0,
    y_alvo=2.0,
    dist_frente=0.3,
    dist_esq=2.5,
    dist_dir=1.0
)

print("\nTESTE 2")
print(f"Estado: {resultado[0]}")
print(f"v = {resultado[1]:.2f} m/s")
print(f"omega = {resultado[2]:.2f} rad/s")


# -----------------------------------------------------
# TESTE 3: Robô chegou ao objetivo
# -----------------------------------------------------

resultado = maquina_de_estados(
    x=1.9,
    y=2.0,
    theta=0.0,
    x_alvo=2.0,
    y_alvo=2.0,
    dist_frente=0.3,
    dist_esq=1.0,
    dist_dir=1.0
)

print("\nTESTE 3")
print(f"Estado: {resultado[0]}")
print(f"v = {resultado[1]:.2f} m/s")
print(f"omega = {resultado[2]:.2f} rad/s")
