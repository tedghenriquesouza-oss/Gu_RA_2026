import pygame
import math

# ============================================================
# EXERCÍCIO 4 - BRAITENBERG
# Conexões diretas: Atração / Agressão
# ============================================================

pygame.init()

# ============================================================
# CONFIGURAÇÕES
# ============================================================

LARGURA = 1000
ALTURA = 700

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Braitenberg - Atração / Agressão")

clock = pygame.time.Clock()

# Cores
FUNDO = (25, 25, 30)
BRANCO = (240, 240, 240)
AZUL = (60, 140, 255)
VERDE = (50, 220, 100)
VERMELHO = (230, 70, 70)
AMARELO = (240, 220, 70)
CINZA = (100, 100, 110)
LARANJA = (255, 150, 50)

fonte = pygame.font.SysFont("Arial", 22)
fonte_pequena = pygame.font.SysFont("Arial", 17)

# ============================================================
# PARÂMETROS DO ROBÔ
# ============================================================

# Velocidade base
v0 = 2.0

# Ganho dos sensores
alpha = 5.0

# Distância máxima dos sensores
d_max = 250.0

# Distância entre as rodas
DIST_RODAS = 50.0

# Raio do robô
RAIO_ROBO = 25

# ============================================================
# POSIÇÃO INICIAL
# ============================================================

x = 250.0
y = ALTURA / 2

# Orientação do robô
theta = 0.0

# ============================================================
# OBSTÁCULO
# ============================================================

obstaculo = pygame.Rect(
    650,
    250,
    100,
    200
)

# ============================================================
# SENSORES
# ============================================================

# Ângulo dos sensores em relação à frente
ANGULO_SENSOR_ESQ = math.radians(-35)
ANGULO_SENSOR_DIR = math.radians(35)


# ============================================================
# FUNÇÃO PARA CALCULAR DISTÂNCIA DO SENSOR
# ============================================================

def medir_sensor(angulo_sensor):
    """
    Faz uma simulação simples de sensor de distância.

    O sensor dispara um raio a partir do robô e procura
    uma interseção com o obstáculo.
    """

    angulo = theta + angulo_sensor

    # Posição inicial do sensor
    sensor_x = x
    sensor_y = y

    # Percorre o raio em pequenos passos
    passo = 2.0

    for distancia in range(
        0,
        int(d_max),
        int(passo)
    ):

        px = sensor_x + math.cos(angulo) * distancia
        py = sensor_y + math.sin(angulo) * distancia

        # Verifica se chegou ao obstáculo
        if obstaculo.collidepoint(
            int(px),
            int(py)
        ):
            return float(distancia)

        # Verifica bordas da arena
        if (
            px < 0
            or px >= LARGURA
            or py < 0
            or py >= ALTURA
        ):
            return d_max

    return d_max


# ============================================================
# CÁLCULO BRAITENBERG
# ============================================================

def calcular_velocidades(d_esq, d_dir):

    # Sensor esquerdo -> roda esquerda
    vL = v0 + alpha * (
        1.0 - d_esq / d_max
    )

    # Sensor direito -> roda direita
    vR = v0 + alpha * (
        1.0 - d_dir / d_max
    )

    # Evita velocidades negativas
    vL = max(0.0, vL)
    vR = max(0.0, vR)

    return vL, vR


# ============================================================
# DESENHAR ROBÔ
# ============================================================

def desenhar_robo():

    # Corpo
    pygame.draw.circle(
        tela,
        AZUL,
        (int(x), int(y)),
        RAIO_ROBO
    )

    pygame.draw.circle(
        tela,
        BRANCO,
        (int(x), int(y)),
        RAIO_ROBO,
        2
    )

    # Direção
    frente_x = (
        x +
        math.cos(theta) *
        RAIO_ROBO
    )

    frente_y = (
        y +
        math.sin(theta) *
        RAIO_ROBO
    )

    pygame.draw.line(
        tela,
        AMARELO,
        (int(x), int(y)),
        (int(frente_x), int(frente_y)),
        5
    )

    # Posição dos sensores
    sensor_esq_x = (
        x +
        math.cos(theta + ANGULO_SENSOR_ESQ)
        * RAIO_ROBO
    )

    sensor_esq_y = (
        y +
        math.sin(theta + ANGULO_SENSOR_ESQ)
        * RAIO_ROBO
    )

    sensor_dir_x = (
        x +
        math.cos(theta + ANGULO_SENSOR_DIR)
        * RAIO_ROBO
    )

    sensor_dir_y = (
        y +
        math.sin(theta + ANGULO_SENSOR_DIR)
        * RAIO_ROBO
    )

    # Sensores
    pygame.draw.circle(
        tela,
        VERDE,
        (int(sensor_esq_x), int(sensor_esq_y)),
        6
    )

    pygame.draw.circle(
        tela,
        VERMELHO,
        (int(sensor_dir_x), int(sensor_dir_y)),
        6
    )


# ============================================================
# DESENHAR RAIOS DOS SENSORES
# ============================================================

def desenhar_sensor(
    angulo_sensor,
    distancia,
    cor
):

    angulo = theta + angulo_sensor

    inicio_x = x
    inicio_y = y

    fim_x = (
        x +
        math.cos(angulo) *
        distancia
    )

    fim_y = (
        y +
        math.sin(angulo) *
        distancia
    )

    pygame.draw.line(
        tela,
        cor,
        (int(inicio_x), int(inicio_y)),
        (int(fim_x), int(fim_y)),
        2
    )


# ============================================================
# LOOP PRINCIPAL
# ============================================================

rodando = True

while rodando:

    dt = clock.tick(60) / 1000.0

    # ========================================================
    # EVENTOS
    # ========================================================

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN:

            # ESC -> sair
            if evento.key == pygame.K_ESCAPE:
                rodando = False

            # R -> reiniciar
            elif evento.key == pygame.K_r:

                x = 250.0
                y = ALTURA / 2
                theta = 0.0

                print("\n>>> ROBÔ REINICIADO <<<\n")


    # ========================================================
    # LEITURA DOS SENSORES
    # ========================================================

    d_esq = medir_sensor(
        ANGULO_SENSOR_ESQ
    )

    d_dir = medir_sensor(
        ANGULO_SENSOR_DIR
    )


    # ========================================================
    # BRAITENBERG
    # ========================================================

    vL, vR = calcular_velocidades(
        d_esq,
        d_dir
    )


    # ========================================================
    # CINEMÁTICA DO ROBÔ DIFERENCIAL
    # ========================================================

    # Velocidade linear do robô
    v = (vR + vL) / 2.0

    # Velocidade angular
    omega = (vR - vL) / DIST_RODAS

    # Atualiza orientação
    theta += omega * dt

    # Atualiza posição
    x += v * math.cos(theta) * 60 * dt
    y += v * math.sin(theta) * 60 * dt


    # ========================================================
    # LIMITES DA ARENA
    # ========================================================

    if x < RAIO_ROBO:
        x = RAIO_ROBO

    if x > LARGURA - RAIO_ROBO:
        x = LARGURA - RAIO_ROBO

    if y < RAIO_ROBO:
        y = RAIO_ROBO

    if y > ALTURA - RAIO_ROBO:
        y = ALTURA - RAIO_ROBO


    # ========================================================
    # DESENHO
    # ========================================================

    tela.fill(FUNDO)

    # Obstáculo
    pygame.draw.rect(
        tela,
        VERMELHO,
        obstaculo
    )

    pygame.draw.rect(
        tela,
        BRANCO,
        obstaculo,
        2
    )

    # Sensores
    desenhar_sensor(
        ANGULO_SENSOR_ESQ,
        d_esq,
        VERDE
    )

    desenhar_sensor(
        ANGULO_SENSOR_DIR,
        d_dir,
        VERMELHO
    )

    # Robô
    desenhar_robo()


    # ========================================================
    # PAINEL DE INFORMAÇÕES
    # ========================================================

    tela.blit(
        fonte.render(
            "BRAITENBERG - ATRAÇÃO / AGRESSÃO",
            True,
            BRANCO
        ),
        (20, 20)
    )

    tela.blit(
        fonte_pequena.render(
            "Conexões diretas: sensor esquerdo -> roda esquerda",
            True,
            VERDE
        ),
        (20, 60)
    )

    tela.blit(
        fonte_pequena.render(
            "Sensor direito -> roda direita",
            True,
            VERMELHO
        ),
        (20, 85)
    )

    # Distâncias
    tela.blit(
        fonte.render(
            f"d_esq = {d_esq:.1f} px",
            True,
            VERDE
        ),
        (20, 130)
    )

    tela.blit(
        fonte.render(
            f"d_dir = {d_dir:.1f} px",
            True,
            VERMELHO
        ),
        (20, 165)
    )

    # Velocidades
    tela.blit(
        fonte.render(
            f"vL = {vL:.2f} px/s",
            True,
            VERDE
        ),
        (20, 215)
    )

    tela.blit(
        fonte.render(
            f"vR = {vR:.2f} px/s",
            True,
            VERMELHO
        ),
        (20, 250)
    )

    # Velocidade angular
    tela.blit(
        fonte.render(
            f"omega = {omega:.3f} rad/s",
            True,
            AZUL
        ),
        (20, 300)
    )

    # Fórmulas
    tela.blit(
        fonte_pequena.render(
            "vL = v0 + alpha * (1 - d_esq / d_max)",
            True,
            BRANCO
        ),
        (20, 360)
    )

    tela.blit(
        fonte_pequena.render(
            "vR = v0 + alpha * (1 - d_dir / d_max)",
            True,
            BRANCO
        ),
        (20, 385)
    )

    # Controles
    tela.blit(
        fonte_pequena.render(
            "R = reiniciar",
            True,
            AMARELO
        ),
        (20, 450)
    )

    tela.blit(
        fonte_pequena.render(
            "ESC = sair",
            True,
            AMARELO
        ),
        (20, 475)
    )

    # Legenda
    tela.blit(
        fonte_pequena.render(
            "VERDE = sensor esquerdo",
            True,
            VERDE
        ),
        (700, 620)
    )

    tela.blit(
        fonte_pequena.render(
            "VERMELHO = sensor direito / obstáculo",
            True,
            VERMELHO
        ),
        (700, 645)
    )

    pygame.display.flip()


pygame.quit()
