import pygame
import math
import numpy as np
import random

LARGURA, ALTURA = 900, 650
FPS = 60

class RoboComSensores:
    def __init__(self, x, y, angulo=0.0):
        self.x = float(x)
        self.y = float(y)
        self.angulo = float(angulo)
        
        # 5 SENSORES: -60°, -30°, 0°, +30°, +60°
        self.angulos_sensores = [
            -math.pi/3,    # -60° (esquerda extrema)
            -math.pi/6,    # -30° (esquerda)
            0.0,           # 0° (frente)
            math.pi/6,     # +30° (direita)
            math.pi/3      # +60° (direita extrema)
        ]
        
        self.nomes_sensores = ["Esq Ext", "Esq", "Frente", "Dir", "Dir Ext"]
        self.alcance_maximo = 300.0
        self.leituras = [self.alcance_maximo] * 5
        self.leituras_ruidosas = [self.alcance_maximo] * 5
        
        # Cores para cada sensor
        self.cores_sensores = [
            (255, 100, 100),   # Vermelho
            (255, 200, 100),   # Laranja
            (255, 255, 100),   # Amarelo
            (100, 255, 100),   # Verde claro
            (100, 200, 255)    # Azul claro
        ]

    def calcular_raios(self, obstaculos):
        """Calcula a distancia de cada sensor com ruido gaussiano"""
        self.leituras = []
        self.leituras_ruidosas = []
        
        for i, beta in enumerate(self.angulos_sensores):
            ang = self.angulo + beta
            dist = self.alcance_maximo
            
            # Raycasting - percorre o raio em passos pequenos
            for passo in range(5, int(self.alcance_maximo), 3):
                rx = self.x + passo * math.cos(ang)
                ry = self.y + passo * math.sin(ang)
                
                # Verifica bordas da tela
                if rx <= 0 or rx >= LARGURA or ry <= 0 or ry >= ALTURA:
                    dist = float(passo)
                    break
                
                # Verifica colisão com obstáculos
                colidiu = False
                for obs in obstaculos:
                    if obs.collidepoint(rx, ry):
                        dist = float(passo)
                        colidiu = True
                        break
                if colidiu:
                    break
            
            # Armazena leitura sem ruido
            self.leituras.append(dist)
            
            # ADICIONA RUIDO GAUSSIANO (media=0, desvio=2.0)
            ruido = np.random.normal(0, 2.0)
            dist_com_ruido = dist + ruido
            
            # Garante que a distancia nao ultrapasse o alcance maximo
            if dist_com_ruido > self.alcance_maximo:
                dist_com_ruido = self.alcance_maximo
            if dist_com_ruido < 0:
                dist_com_ruido = 0
                
            self.leituras_ruidosas.append(dist_com_ruido)

    def desenhar(self, tela, mostrar_ruido=True):
        """Desenha o robo, os raios e os valores dos sensores"""
        fonte = pygame.font.SysFont("monospace", 12)
        fonte_valor = pygame.font.SysFont("monospace", 14, bold=True)
        
        # Desenha cada raio sensor
        for i, beta in enumerate(self.angulos_sensores):
            ang = self.angulo + beta
            
            # Escolhe qual distancia usar (com ou sem ruido)
            if mostrar_ruido:
                dist = self.leituras_ruidosas[i]
            else:
                dist = self.leituras[i]
            
            # Ponto final do raio
            rx = self.x + dist * math.cos(ang)
            ry = self.y + dist * math.sin(ang)
            
            cor = self.cores_sensores[i]
            
            # Desenha o raio (linha)
            if dist < self.alcance_maximo:
                # Raio que colidiu - mais brilhante
                pygame.draw.line(tela, cor, (int(self.x), int(self.y)), (int(rx), int(ry)), 3)
                # Circulo no ponto de colisao
                pygame.draw.circle(tela, (255, 255, 255), (int(rx), int(ry)), 5)
                pygame.draw.circle(tela, cor, (int(rx), int(ry)), 3)
            else:
                # Raio livre - mais transparente
                pygame.draw.line(tela, (cor[0]//2, cor[1]//2, cor[2]//2), 
                               (int(self.x), int(self.y)), (int(rx), int(ry)), 2)
                pygame.draw.circle(tela, cor, (int(rx), int(ry)), 3)
            
            # --- RENDERIZA O VALOR DO SENSOR AO LADO DO RAIO ---
            # Posicao do texto (no meio do raio)
            meio_x = (self.x + rx) / 2
            meio_y = (self.y + ry) / 2
            
            # Desvia um pouco o texto para nao ficar em cima da linha
            offset_x = -20 * math.sin(ang)
            offset_y = 20 * math.cos(ang)
            
            # Se o raio for curto, coloca o texto mais perto do robo
            if dist < 50:
                tx = self.x + 30 * math.cos(ang) + offset_x
                ty = self.y + 30 * math.sin(ang) + offset_y
            else:
                tx = meio_x + offset_x
                ty = meio_y + offset_y
            
            # Formata o valor com e sem ruido
            if mostrar_ruido:
                valor_original = self.leituras[i]
                valor_ruidoso = self.leituras_ruidosas[i]
                
                if dist < self.alcance_maximo:
                    texto = f"{self.nomes_sensores[i]}: {valor_ruidoso:.1f}px"
                    cor_texto = (255, 255, 255)
                else:
                    texto = f"{self.nomes_sensores[i]}: >{self.alcance_maximo:.0f}px"
                    cor_texto = (150, 150, 150)
                
                # Mostra o ruido em uma linha menor
                texto_ruido = f"±{abs(valor_ruidoso - valor_original):.1f}"
                
                # Renderiza o texto principal
                txt_superficie = fonte_valor.render(texto, True, cor_texto)
                tela.blit(txt_superficie, (int(tx - txt_superficie.get_width()/2), int(ty - 10)))
                
                # Renderiza o ruido em vermelho (menor)
                txt_ruido = fonte.render(texto_ruido, True, (255, 100, 100))
                tela.blit(txt_ruido, (int(tx - txt_ruido.get_width()/2), int(ty + 15)))
            else:
                # Versao sem ruido
                if dist < self.alcance_maximo:
                    texto = f"{self.nomes_sensores[i]}: {dist:.1f}px"
                    cor_texto = (200, 200, 200)
                else:
                    texto = f"{self.nomes_sensores[i]}: >{self.alcance_maximo:.0f}px"
                    cor_texto = (100, 100, 100)
                
                txt_superficie = fonte.render(texto, True, cor_texto)
                tela.blit(txt_superficie, (int(tx - txt_superficie.get_width()/2), int(ty - 5)))
        
        # Desenha o corpo do robo
        pos = (int(self.x), int(self.y))
        
        # Circulo externo com cores dos sensores
        for i, beta in enumerate(self.angulos_sensores):
            ang = self.angulo + beta
            px = self.x + 22 * math.cos(ang)
            py = self.y + 22 * math.sin(ang)
            pygame.draw.circle(tela, self.cores_sensores[i], (int(px), int(py)), 4)
        
        pygame.draw.circle(tela, (0, 200, 255), pos, 20)
        pygame.draw.circle(tela, (100, 220, 255), pos, 20, 2)
        
        # Seta de orientacao
        fx = self.x + 30 * math.cos(self.angulo)
        fy = self.y + 30 * math.sin(self.angulo)
        pygame.draw.line(tela, (255, 50, 50), pos, (int(fx), int(fy)), 4)
        
        # Circulo central
        pygame.draw.circle(tela, (255, 255, 255), pos, 6)

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("LAB 03 - 5 Sensores com Ruido Gaussiano")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont("monospace", 14)
    fonte_titulo = pygame.font.SysFont("monospace", 16, bold=True)

    robo = RoboComSensores(LARGURA/2, ALTURA/2, 0.0)
    
    # Obstaculos variados para testar os sensores
    obstaculos = [
        pygame.Rect(300, 100, 120, 200),   # Obstaculo esquerdo
        pygame.Rect(550, 80, 150, 150),    # Obstaculo frente-esquerda
        pygame.Rect(700, 300, 100, 250),   # Obstaculo direita
        pygame.Rect(400, 450, 200, 100),   # Obstaculo frente-direita
        pygame.Rect(100, 400, 80, 150)     # Obstaculo esquerda-baixo
    ]

    mostrar_ruido = True
    seguir_mouse = True
    rodando = True

    while rodando:
        relogio.tick(FPS)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    # Alterna mostrar ruido
                    mostrar_ruido = not mostrar_ruido
                    print(f"Mostrar ruido: {mostrar_ruido}")
                
                if evento.key == pygame.K_m:
                    # Alterna seguir mouse
                    seguir_mouse = not seguir_mouse
                    print(f"Seguir mouse: {seguir_mouse}")
                
                if evento.key == pygame.K_SPACE:
                    # Reseta posicao
                    robo = RoboComSensores(LARGURA/2, ALTURA/2, 0.0)
                    print("Robo resetado")
                
                if evento.key == pygame.K_ESCAPE:
                    rodando = False

        # Segue o mouse
        if seguir_mouse:
            mx, my = pygame.mouse.get_pos()
            dx, dy = mx - robo.x, my - robo.y
            if dx != 0 or dy != 0:
                robo.angulo = math.atan2(dy, dx)
                robo.x += dx * 0.04
                robo.y += dy * 0.04

        robo.calcular_raios(obstaculos)

        # Limpa tela
        tela.fill((20, 24, 30))
        
        # Desenha obstaculos
        for obs in obstaculos:
            pygame.draw.rect(tela, (180, 50, 50), obs)
            pygame.draw.rect(tela, (255, 100, 100), obs, 2)
        
        # Desenha robo
        robo.desenhar(tela, mostrar_ruido)

        # Painel de informacoes
        y = 10
        infos = [
            ("LAB 03 - MULTIPLOS SENSORES", (100, 200, 255)),
            ("", None),
            (f"Status: {'Seguindo mouse' if seguir_mouse else 'Parado'}", (220, 220, 220)),
            (f"Mostrar ruido: {'SIM' if mostrar_ruido else 'NAO'}", (255, 215, 0) if mostrar_ruido else (150, 150, 150)),
            ("", None),
            ("LEITURAS DOS SENSORES:", (200, 200, 200)),
        ]
        
        for i, (info, cor) in enumerate(infos):
            if info:
                if cor:
                    texto = fonte.render(info, True, cor)
                else:
                    texto = fonte.render(info, True, (220, 220, 220))
                tela.blit(texto, (15, y + i * 22))
        
        # Mostra leituras individuais com cores
        y_base = 10 + len(infos) * 22
        for i, nome in enumerate(robo.nomes_sensores):
            cor = robo.cores_sensores[i]
            if mostrar_ruido:
                valor = robo.leituras_ruidosas[i]
                original = robo.leituras[i]
                if valor < robo.alcance_maximo:
                    texto = f"{nome}: {valor:.1f}px (ruido: ±{abs(valor-original):.1f})"
                else:
                    texto = f"{nome}: >{robo.alcance_maximo:.0f}px"
            else:
                valor = robo.leituras[i]
                if valor < robo.alcance_maximo:
                    texto = f"{nome}: {valor:.1f}px"
                else:
                    texto = f"{nome}: >{robo.alcance_maximo:.0f}px"
            
            # Cor do texto baseada na distancia
            if robo.leituras[i] < 100:
                cor_texto = (255, 50, 50)  # Vermelho - perto
            elif robo.leituras[i] < 200:
                cor_texto = (255, 200, 50)  # Amarelo - medio
            else:
                cor_texto = (50, 255, 50)   # Verde - longe
            
            texto_sensor = fonte.render(texto, True, cor_texto)
            tela.blit(texto_sensor, (20, y_base + i * 20))

        # Legenda no canto inferior
        y_legenda = ALTURA - 80
        legenda_titulo = fonte_titulo.render("CONTROLES:", True, (200, 200, 200))
        tela.blit(legenda_titulo, (20, y_legenda))
        
        controles = [
            "[R] Alternar ruido",
            "[M] Seguir/Parar mouse",
            "[SPACE] Resetar posicao",
            "[ESC] Sair"
        ]
        
        for i, ctrl in enumerate(controles):
            txt = fonte.render(ctrl, True, (150, 150, 150))
            tela.blit(txt, (30, y_legenda + 25 + i * 18))

        # Mostra posicao do mouse
        mx, my = pygame.mouse.get_pos()
        pos_mouse = fonte.render(f"Mouse: ({int(mx)}, {int(my)})", True, (100, 100, 100))
        tela.blit(pos_mouse, (LARGURA - 180, ALTURA - 25))

        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()