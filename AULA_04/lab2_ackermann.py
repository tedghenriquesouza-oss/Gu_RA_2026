import pygame
import math

pygame.init()

# ============================================================
# CONFIGURAÇÕES
# ============================================================

LARGURA = 500
ALTURA = 500

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Ackermann - Calculadora de Giro")

clock = pygame.time.Clock()

# Parâmetros do veículo
L = 2.0
PHI_MAX = 30.0

# Valores iniciais
v = 1.0
phi = 0.0

# Posição inicial
x = LARGURA // 2
y = ALTURA // 2
theta = 0.0

trajetoria = []

ESCALA = 80

# Cores
FUNDO = (25, 25, 30)
BRANCO = (240, 240, 240)
VERDE = (50, 220, 100)
AZUL = (70, 150, 255)
AMARELO = (240, 220, 70)

fonte = pygame.font.SysFont("Arial", 22)
fonte_pequena = pygame.font.SysFont("Arial", 18)


# ============================================================
# CÁLCULO ACKERMANN
# ============================================================

def calcular_ackermann(v, phi):

    phi_rad = math.radians(phi)

    if abs(phi_rad) < 1e-9:

        omega = 0.0
        raio = float("inf")

    else:

        omega = (v / L) * math.tan(phi_rad)
        raio = L / abs(math.tan(phi_rad))

    return omega, raio


# ============================================================
# MOSTRAR RESULTADO NO TERMINAL
# ============================================================

def mostrar_resultado():

    omega, raio = calcular_ackermann(v, phi)

    print("\n==========================================")
    print("        CALCULADORA ACKERMANN")
    print("==========================================")

    print(f"Velocidade linear (v): {v:.2f} m/s")
    print(f"Ângulo de esterço (φ): {phi:.2f} graus")
    print(f"Entre-eixos (L): {L:.2f} m")

    print("------------------------------------------")

    print(f"Velocidade angular (ω): {omega:.4f} rad/s")

    if math.isinf(raio):
        print("Raio de curvatura (R): infinito")
        print("Trajetória: LINHA RETA")
    else:
        print(f"Raio de curvatura (R): {raio:.4f} m")

        if phi > 0:
            print("Sentido da curva: ESQUERDA")
        elif phi < 0:
            print("Sentido da curva: DIREITA")

    print("------------------------------------------")

    print("Limite de esterço: ±30°")

    if abs(phi) == PHI_MAX:

        print("ESTERÇO MÁXIMO ATINGIDO!")

    if raio != float("inf"):

        print(
            f"Raio mínimo possível com ±30°: "
            f"{L / math.tan(math.radians(PHI_MAX)):.4f} m"
        )

    print("==========================================\n")


# ============================================================
# DESENHAR VEÍCULO
# ============================================================

def desenhar_veiculo(x, y, theta):

    comprimento = 70
    largura = 35

    pontos = [
        (-comprimento / 2, -largura / 2),
        (comprimento / 2, -largura / 2),
        (comprimento / 2, largura / 2),
        (-comprimento / 2, largura / 2)
    ]

    pontos_tela = []

    for px, py in pontos:

        rx = px * math.cos(theta) - py * math.sin(theta)
        ry = px * math.sin(theta) + py * math.cos(theta)

        pontos_tela.append(
            (x + rx, y + ry)
        )

    pygame.draw.polygon(
        tela,
        AZUL,
        pontos_tela
    )

    pygame.draw.polygon(
        tela,
        BRANCO,
        pontos_tela,
        2
    )


# ============================================================
# PRIMEIRO RESULTADO
# ============================================================

mostrar_resultado()


# ============================================================
# LOOP PRINCIPAL
# ============================================================

rodando = True

while rodando:

    dt = clock.tick(60) / 1000.0

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN:

            # Sair
            if evento.key == pygame.K_ESCAPE:
                rodando = False

            # Aumentar velocidade
            elif evento.key == pygame.K_UP:

                v += 0.2
                mostrar_resultado()

            # Diminuir velocidade
            elif evento.key == pygame.K_DOWN:

                v -= 0.2
                v = max(0, v)

                mostrar_resultado()

            # Esterçar para esquerda
            elif evento.key == pygame.K_LEFT:

                phi -= 2

                if phi < -PHI_MAX:
                    phi = -PHI_MAX

                mostrar_resultado()

            # Esterçar para direita
            elif evento.key == pygame.K_RIGHT:

                phi += 2

                if phi > PHI_MAX:
                    phi = PHI_MAX

                mostrar_resultado()

            # Centralizar rodas
            elif evento.key == pygame.K_SPACE:

                phi = 0

                mostrar_resultado()

            # Reiniciar
            elif evento.key == pygame.K_r:

                x = LARGURA // 2
                y = ALTURA // 2
                theta = 0
                trajetoria.clear()

                print("\n>>> TRAJETÓRIA REINICIADA <<<\n")


    # ========================================================
    # CINEMÁTICA
    # ========================================================

    omega, raio = calcular_ackermann(v, phi)

    theta += omega * dt

    x += (
        v * ESCALA *
        math.cos(theta) *
        dt
    )

    y += (
        v * ESCALA *
        math.sin(theta) *
        dt
    )

    trajetoria.append(
        (int(x), int(y))
    )

    if len(trajetoria) > 10000:
        trajetoria.pop(0)


    # ========================================================
    # DESENHO
    # ========================================================

    tela.fill(FUNDO)

    # Grade
    for gx in range(0, LARGURA, ESCALA):
        pygame.draw.line(
            tela,
            (40, 40, 45),
            (gx, 0),
            (gx, ALTURA)
        )

    for gy in range(0, ALTURA, ESCALA):
        pygame.draw.line(
            tela,
            (40, 40, 45),
            (0, gy),
            (LARGURA, gy)
        )

    # Trajetória
    if len(trajetoria) > 1:

        pygame.draw.lines(
            tela,
            VERDE,
            False,
            trajetoria,
            3
        )

    # Veículo
    desenhar_veiculo(
        x,
        y,
        theta
    )


    # ========================================================
    # INFORMAÇÕES NA TELA
    # ========================================================

    omega, raio = calcular_ackermann(v, phi)

    tela.blit(
        fonte.render(
            "CALCULADORA ACKERMANN",
            True,
            BRANCO
        ),
        (20, 20)
    )

    tela.blit(
        fonte.render(
            f"v = {v:.2f} m/s",
            True,
            BRANCO
        ),
        (20, 60)
    )

    tela.blit(
        fonte.render(
            f"phi = {phi:.1f} graus",
            True,
            BRANCO
        ),
        (20, 95)
    )

    tela.blit(
        fonte.render(
            f"omega = {omega:.3f} rad/s",
            True,
            AZUL
        ),
        (20, 130)
    )

    if math.isinf(raio):

        texto = "R = infinito (reta)"

    else:

        texto = f"R = {raio:.2f} m"

    tela.blit(
        fonte.render(
            texto,
            True,
            AMARELO
        ),
        (20, 165)
    )

    tela.blit(
        fonte_pequena.render(
            "UP/DOWN = velocidade",
            True,
            BRANCO
        ),
        (20, 220)
    )

    tela.blit(
        fonte_pequena.render(
            "LEFT/RIGHT = esterço",
            True,
            BRANCO
        ),
        (20, 245)
    )

    tela.blit(
        fonte_pequena.render(
            "SPACE = esterço 0°",
            True,
            BRANCO
        ),
        (20, 270)
    )

    tela.blit(
        fonte_pequena.render(
            "R = reiniciar trajetória",
            True,
            BRANCO
        ),
        (20, 295)
    )

    tela.blit(
        fonte_pequena.render(
            "ESC = sair",
            True,
            BRANCO
        ),
        (20, 320)
    )

    pygame.display.flip()


pygame.quit()
