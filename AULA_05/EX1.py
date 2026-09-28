def converter_cmd_vel(v, omega, L=0.3, max_wheel_speed=1.5):
    """
    Converte velocidade linear e angular em velocidades
    das rodas esquerda e direita de um robô diferencial.

    Parâmetros:
        v: velocidade linear (m/s)
        omega: velocidade angular (rad/s)
        L: distância entre as rodas (m)
        max_wheel_speed: velocidade máxima das rodas (m/s)

    Retorna:
        v_e: velocidade da roda esquerda (m/s)
        v_d: velocidade da roda direita (m/s)
    """

    # 1. Calcula as velocidades brutas das rodas
    v_e = v - (omega * L / 2)
    v_d = v + (omega * L / 2)

    # Mostra os valores antes da saturação
    print("Velocidades brutas:")
    print(f"Roda esquerda: {v_e:.2f} m/s")
    print(f"Roda direita:  {v_d:.2f} m/s")

    # 2. Verifica a maior velocidade em módulo
    maior_velocidade = max(abs(v_e), abs(v_d))

    # 3. Saturação proporcional
    if maior_velocidade > max_wheel_speed:

        fator = max_wheel_speed / maior_velocidade

        v_e = v_e * fator
        v_d = v_d * fator

        print("\nSaturação aplicada!")
        print(f"Fator de redução: {fator:.4f}")

    else:
        print("\nNenhuma saturação necessária.")

    return v_e, v_d


# =====================================================
# TESTE DO PROGRAMA
# =====================================================

v = 1.2          # velocidade linear em m/s
omega = 3.0      # velocidade angular em rad/s
L = 0.3          # distância entre as rodas em metros
max_wheel_speed = 1.5  # velocidade máxima das rodas


# Chama a função
v_e, v_d = converter_cmd_vel(
    v,
    omega,
    L,
    max_wheel_speed
)


# Mostra o resultado final
print("\nVelocidades finais das rodas:")
print(f"Roda esquerda: {v_e:.2f} m/s")
print(f"Roda direita:  {v_d:.2f} m/s")
