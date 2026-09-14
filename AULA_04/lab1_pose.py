import math
import pygame

# ============================================================
# CONFIGURAÇÃO
# ============================================================

# Pose inicial
x = 0.0
y = 0.0
theta = 0.0

# Sequência de comandos:
# (tempo, velocidade linear, velocidade angular)
comandos = [
    (4.0, 0.5, 0.0),
    (2.0, 0.0, 0.7854),
    (3.0, 0.4, 0.0)
]


# ============================================================
# CINEMÁTICA DIFERENCIAL
# ============================================================

def atualizar_pose(x, y, theta, v, omega, dt):
    """
    Atualiza a pose do robô usando a cinemática diferencial.

    x, y     -> posição do robô
    theta    -> orientação em radianos
    v        -> velocidade linear (m/s)
    omega    -> velocidade angular (rad/s)
    dt       -> intervalo de tempo (s)
    """

    x = x + v * math.cos(theta) * dt
    y = y + v * math.sin(theta) * dt
    theta = theta + omega * dt

    return x, y, theta


# ============================================================
# CÁLCULO DA POSE TEÓRICA
# ============================================================

print("=== POSE TEÓRICA ===")

for tempo, v, omega in comandos:

    x, y, theta = atualizar_pose(
        x, y, theta, v, omega, tempo
    )

    print(
        f"Trecho: {tempo:.1f}s | "
        f"v={v:.4f} m/s | "
        f"omega={omega:.4f} rad/s"
    )

    print(
        f"Pose: x={x:.4f} m, "
        f"y={y:.4f} m, "
        f"theta={theta:.4f} rad"
    )


pose_teorica = (x, y, theta)

print("\nPose final teórica:")
print(f"x     = {x:.4f} m")
print(f"y     = {y:.4f} m")
print(f"theta = {theta:.4f} rad")
print(f"theta = {math.degrees(theta):.2f} graus")


# ============================================================
# SIMULAÇÃO PYGAME
# ============================================================

pygame.init()

LARGURA = 1000
ALTURA = 1000

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Lab 1 - Validador de Pose")

clock = pygame.time.Clock()

# Pose simulada
x_sim = 0.0
y_sim = 0.0
theta_sim = 0.0

# Escala: pixels por metro
ESCALA = 80

# Centro do mundo
CX = LARGURA // 2
CY = ALTURA // 2

# Controle dos trechos
indice = 0
tempo_trecho = 0.0

rodando = True

while rodando:

    # Tempo real decorrido
    dt = clock.tick(60) / 1000.0

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

    # ========================================================
    # EXECUÇÃO DOS COMANDOS
    # ========================================================

    if indice < len(comandos):

        tempo_total, v, omega = comandos[indice]

        # Evita ultrapassar o tempo do trecho
        dt_comando = min(dt, tempo_total - tempo_trecho)

        x_sim, y_sim, theta_sim = atualizar_pose(
            x_sim,
            y_sim,
            theta_sim,
            v,
            omega,
            dt_comando
        )

        tempo_trecho += dt_comando

        # Próximo trecho
        if tempo_trecho >= tempo_total:
            indice += 1
            tempo_trecho = 0.0

    # ========================================================
    # DESENHO
    # ========================================================

    tela.fill((30, 30, 30))

    # Origem do mundo
    pygame.draw.line(
        tela,
        (70, 70, 70),
        (0, CY),
        (LARGURA, CY)
    )

    pygame.draw.line(
        tela,
        (70, 70, 70),
        (CX, 0),
        (CX, ALTURA)
    )

    # Conversão mundo -> tela
    px = CX + int(x_sim * ESCALA)
    py = CY - int(y_sim * ESCALA)

    # Corpo do robô
    tamanho = 20

    pontos = [
        (
            px + tamanho * math.cos(theta_sim),
            py - tamanho * math.sin(theta_sim)
        ),
        (
            px + tamanho * math.cos(theta_sim + 2.4),
            py - tamanho * math.sin(theta_sim + 2.4)
        ),
        (
            px + tamanho * math.cos(theta_sim - 2.4),
            py - tamanho * math.sin(theta_sim - 2.4)
        )
    ]

    pygame.draw.polygon(
        tela,
        (0, 180, 255),
        pontos
    )

    # Linha indicando a orientação
    fim_x = px + int(35 * math.cos(theta_sim))
    fim_y = py - int(35 * math.sin(theta_sim))

    pygame.draw.line(
        tela,
        (255, 0, 0),
        (px, py),
        (fim_x, fim_y),
        3
    )

    # Informações na tela
    fonte = pygame.font.SysFont(None, 28)

    texto = fonte.render(
        f"x={x_sim:.2f}  y={y_sim:.2f}  "
        f"theta={math.degrees(theta_sim):.1f}°",
        True,
        (255, 255, 255)
    )

    tela.blit(texto, (20, 20))

    pygame.display.flip()


pygame.quit()

# ============================================================
# RESULTADO DA SIMULAÇÃO
# ============================================================

print("\n=== POSE SIMULADA ===")
print(f"x     = {x_sim:.4f} m")
print(f"y     = {y_sim:.4f} m")
print(f"theta = {theta_sim:.4f} rad")
print(f"theta = {math.degrees(theta_sim):.2f} graus")

print("\n=== ERRO ===")
print(f"Erro em x     = {x_sim - pose_teorica[0]:.6f} m")
print(f"Erro em y     = {y_sim - pose_teorica[1]:.6f} m")
print(f"Erro em theta = {theta_sim - pose_teorica[2]:.6f} rad")
