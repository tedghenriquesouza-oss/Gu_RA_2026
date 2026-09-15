import pygame
import math
import numpy as np
import sys

def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Filtro de Sensor")
    font = pygame.font.SysFont("consolas", 18)
    clock = pygame.time.Clock()

    num_beams = 7
    fov = math.pi
    angles = np.linspace(-fov/2, fov/2, num_beams)
    robot_pos = (400, 500)

    time_step = 0.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((25, 25, 25))
        time_step += 0.03

        header = font.render("Beam | Raw Noisy Dist | Filtered Dist", True, (255, 255, 255))
        screen.blit(header, (20, 20))
        pygame.draw.line(screen, (255, 255, 255), (20, 45), (400, 45), 1)

        for i, angle in enumerate(angles):
            d_real = 110 + 110 * math.sin(time_step + i * 0.5)

            d_noise = d_real + np.random.normal(0, 5.0)

            if d_noise < 10.0:
                d_filtered_text = "Discarded (< 10.0)"
                draw_dist = 0.0
            elif d_noise > 200.0:
                d_filtered_text = "200.0 (Capped)"
                draw_dist = 200.0
            else:
                d_filtered_text = f"{d_noise:.1f}"
                draw_dist = d_noise

            raw_text = f"{d_noise:5.1f}"
            row_text = font.render(f"  {i+1}  |    {raw_text:>7}   | {d_filtered_text}", True, (200, 200, 200))
            screen.blit(row_text, (20, 55 + i * 30))

            draw_angle = angle - math.pi/2
            
            raw_end_x = robot_pos[0] + max(0, d_noise) * math.cos(draw_angle)
            raw_end_y = robot_pos[1] + max(0, d_noise) * math.sin(draw_angle)
            pygame.draw.line(screen, (150, 50, 50), robot_pos, (raw_end_x, raw_end_y), 1)

            if draw_dist > 0:
                end_x = robot_pos[0] + draw_dist * math.cos(draw_angle)
                end_y = robot_pos[1] + draw_dist * math.sin(draw_angle)
                pygame.draw.line(screen, (50, 200, 50), robot_pos, (end_x, end_y), 3)
                pygame.draw.circle(screen, (50, 200, 50), (int(end_x), int(end_y)), 5)

        pygame.draw.circle(screen, (100, 150, 255), robot_pos, 10)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()