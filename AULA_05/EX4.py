import math


def calcular_orientacao_alvo(x, y, theta, x_alvo, y_alvo, Kp=1.5):
    """
    Calcula a velocidade angular necessária para orientar
    o robô em direção ao alvo.

    Parâmetros:
        x, y: posição atual do robô
        theta: orientação atual do robô (rad)
        x_alvo, y_alvo: posição do alvo
        Kp: ganho proporcional

    Retorna:
        omega: velocidade angular (rad/s)
    """

    # 1. Calcula o ângulo desejado até o alvo
    theta_alvo = math.atan2(
        y_alvo - y,
        x_alvo - x
    )

    # 2. Calcula o erro de orientação
    e_theta = theta_alvo - theta

    # Normaliza o erro para o intervalo [-pi, pi]
    while e_theta > math.pi:
        e_theta -= 2 * math.pi

    while e_theta < -math.pi:
        e_theta += 2 * math.pi

    # 3. Controle proporcional
    omega = Kp * e_theta

    return omega


# =====================================================
# TESTE 1
# =====================================================

# Robô está em (0, 0)
# Orientação atual: 0 rad
# Alvo: (2, 2)

omega = calcular_orientacao_alvo(
    x=0.0,
    y=0.0,
    theta=0.0,
    x_alvo=2.0,
    y_alvo=2.0
)

print("Teste 1:")
print(f"Velocidade angular: {omega:.2f} rad/s")


# =====================================================
# TESTE 2
# =====================================================

# Robô está apontando para cima (pi/2)
# Alvo está à direita

omega = calcular_orientacao_alvo(
    x=0.0,
    y=0.0,
    theta=math.pi / 2,
    x_alvo=2.0,
    y_alvo=0.0
)

print("\nTeste 2:")
print(f"Velocidade angular: {omega:.2f} rad/s")
