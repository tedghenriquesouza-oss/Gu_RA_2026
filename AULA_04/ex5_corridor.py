import pygame
import math
import sys

WIDTH, HEIGHT = 800, 600
FPS = 60


BG_COLOR = (30, 30, 30)
WALL_COLOR = (200, 200, 200)
ROBOT_COLOR = (0, 150, 255)
RAY_COLOR = (255, 50, 50)
TEXT_COLOR = (255, 255, 255)


V_LINEAR = 40.0   
KP = 0.01         


def cast_ray(x, y, angle, walls):
    x1, y1 = x, y
    # Define um raio longo o suficiente para sempre cruzar as paredes visíveis
    x2, y2 = x + math.cos(angle) * 2000, y + math.sin(angle) * 2000
    
    min_d = float('inf')
    closest_pt = None
    
    for wall in walls:
        x3, y3 = wall[0]
        x4, y4 = wall[1]
        
        
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            continue # Linhas paralelas
            
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / denom
        
        
        if 0 <= t <= 1 and 0 <= u <= 1:
            px = x1 + t * (x2 - x1)
            py = y1 + t * (y2 - y1)
            dist = math.hypot(px - x, py - y)
            
            if dist < min_d:
                min_d = dist
                closest_pt = (px, py)
                
    return min_d, closest_pt


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Controle em Malha Fechada: Navegação em Corredor")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

  
    walls = [
        ((0, 200), (WIDTH, 200)),
        ((0, 400), (WIDTH, 400))
    ]


    x, y = 50.0, 350.0 
    theta = 0.0 # Apontando para a direita (0 radianos)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0 # dt em segundos

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        angle_esq = theta - math.pi / 2
        angle_dir = theta + math.pi / 2

        d_esq, pt_esq = cast_ray(x, y, angle_esq, walls)
        d_dir, pt_dir = cast_ray(x, y, angle_dir, walls)

        # Prevenção caso o raio não atinja nada
        if d_esq == float('inf'): d_esq = 0
        if d_dir == float('inf'): d_dir = 0

        e = d_esq - d_dir
        w = KP * e

        x += V_LINEAR * math.cos(theta) * dt
        y += V_LINEAR * math.sin(theta) * dt

        theta -= w * dt


        if x > WIDTH:
            x = 0.0

        # ==========================================
        # Renderização
        # ==========================================
        screen.fill(BG_COLOR)

        # Desenhar Paredes
        for wall in walls:
            pygame.draw.line(screen, WALL_COLOR, wall[0], wall[1], 5)

        # Desenhar os Raios dos Sensores
        if pt_esq:
            pygame.draw.line(screen, RAY_COLOR, (x, y), pt_esq, 1)
            pygame.draw.circle(screen, RAY_COLOR, (int(pt_esq[0]), int(pt_esq[1])), 4)
        if pt_dir:
            pygame.draw.line(screen, RAY_COLOR, (x, y), pt_dir, 1)
            pygame.draw.circle(screen, RAY_COLOR, (int(pt_dir[0]), int(pt_dir[1])), 4)

        # Desenhar Robô (Círculo)
        pygame.draw.circle(screen, ROBOT_COLOR, (int(x), int(y)), 15)
        # Linha de orientação (Heading)
        hx = x + math.cos(theta) * 20
        hy = y + math.sin(theta) * 20
        pygame.draw.line(screen, (0, 255, 0), (x, y), (hx, hy), 3)

        # Exibir Dados e Telemetria
        info = [
            f"Velocidade Linear (v): {V_LINEAR} px/s",
            f"Ganho (Kp): {KP}",
            f"Distância Esq (d_esq): {d_esq:.1f} px",
            f"Distância Dir (d_dir): {d_dir:.1f} px",
            f"Erro (e = d_esq - d_dir): {e:.1f}",
            f"Controle (w = Kp * e): {w:.3f} rad/s"
        ]
        
        for i, text in enumerate(info):
            text_surface = font.render(text, True, TEXT_COLOR)
            screen.blit(text_surface, (10, 10 + i * 25))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()