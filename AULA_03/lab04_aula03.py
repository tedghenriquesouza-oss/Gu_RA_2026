import pygame
import math
import numpy as np
import random

LARGURA, ALTURA = 900, 650
FPS = 60

class RoboBraitenberg:
    def __init__(self, x, y, angulo=0.0):
        self.x = float(x)
        self.y = float(y)
        self.angulo = float(angulo)
        
        # Velocidades
        self.velocidade_base = 2.0  # Velocidade de cruzeiro
        self.vel_esquerda = 0.0
        self.vel_direita = 0.0
        
        # Sensores (5 feixes)
        self.angulos_sensores = [
            -math.pi/3,    # -60° (esquerda extrema)
            -math.pi/6,    # -30° (esquerda)
            0.0,           # 0° (frente)
            math.pi/6,     # +30° (direita)
            math.pi/3      # +60° (direita extrema)
        ]
        
        self.nomes_sensores = ["Esq Ext", "Esq", "Frente", "Dir", "Dir Ext"]
        self.alcance_maximo = 250.0
        self.leituras = [self.alcance_maximo] * 5
        self.leituras_ruidosas = [self.alcance_maximo] * 5
        
        # Limiar para giro de emergencia
        self.limiar_emergencia = 80.0  # Se sensor central < 80px, gira
        
        # Cores dos sensores
        self.cores_sensores = [
            (255, 100, 100),
            (255, 200, 100),
            (255, 255, 100),
            (100, 255, 100),
            (100, 200, 255)
        ]
        
        # Histórico para depuração
        self.ultimo_comando = ""
        
    def calcular_sensores(self, obstaculos):
        """Calcula as leituras dos 5 sensores com ruído gaussiano"""
        self.leituras = []
        self.leituras_ruidosas = []
        
        for beta in self.angulos_sensores:
            ang = self.angulo + beta
            dist = self.alcance_maximo
            
            # Raycasting
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
            
            self.leituras.append(dist)
            
            # Ruído gaussiano
            ruido = np.random.normal(0, 2.0)
            dist_ruido = dist + ruido
            
            if dist_ruido > self.alcance_maximo:
                dist_ruido = self.alcance_maximo
            if dist_ruido < 0:
                dist_ruido = 0
                
            self.leituras_ruidosas.append(dist_ruido)
    
    def controle_braitenberg(self):
        """
        Lei de Braitenberg - Comportamento de Medo Puro
        
        Roda esquerdA acelera com sensores da DIREITA (inverte para desviar)
        Roda direitA acelera com sensores da ESQUERDA (inverte para desviar)
        """
        # Usa leituras com ruído para decisão
        s_esq_ext = self.leituras_ruidosas[0]  # Sensor esquerdo extremo
        s_esq = self.leituras_ruidosas[1]      # Sensor esquerdo
        s_frente = self.leituras_ruidosas[2]   # Sensor frontal
        s_dir = self.leituras_ruidosas[3]      # Sensor direito
        s_dir_ext = self.leituras_ruidosas[4]  # Sensor direito extremo
        
        # --- VERIFICA EMERGÊNCIA (sensor frontal) ---
        if s_frente < self.limiar_emergencia:
            # Giro imediato no próprio eixo (inverte roda esquerda)
            self.vel_esquerda = -self.velocidade_base * 1.5
            self.vel_direita = self.velocidade_base * 1.5
            self.ultimo_comando = "EMERGENCIA - Girando no eixo"
            return
        
        # --- CONTROLE REATIVO DE BRAITENBERG ---
        # Aceleração proporcional à PROXIMIDADE (quanto menor distância, maior aceleração)
        # Usa sensores da DIREITA para controlar roda ESQUERDA
        # Usa sensores da ESQUERDA para controlar roda DIREITA
        
        # Normaliza as distâncias (0 = perto, 1 = longe)
        # Quanto menor a distância, maior o fator de aceleração
        fator_esq = 1.0 - min(s_esq / self.alcance_maximo, 1.0)
        fator_dir = 1.0 - min(s_dir / self.alcance_maximo, 1.0)
        fator_esq_ext = 1.0 - min(s_esq_ext / self.alcance_maximo, 1.0)
        fator_dir_ext = 1.0 - min(s_dir_ext / self.alcance_maximo, 1.0)
        
        # Peso maior para sensores extremos (desvio mais forte)
        # Roda ESQUERDA acelerada por sensores da DIREITA
        aceleracao_esq = (fator_dir * 0.6 + fator_dir_ext * 0.4) * self.velocidade_base
        
        # Roda DIREITA acelerada por sensores da ESQUERDA
        aceleracao_dir = (fator_esq * 0.6 + fator_esq_ext * 0.4) * self.velocidade_base
        
        # Velocidade base + aceleração
        self.vel_esquerda = self.velocidade_base + aceleracao_esq * 1.5
        self.vel_direita = self.velocidade_base + aceleracao_dir * 1.5
        
        # Limita velocidades máximas
        self.vel_esquerda = min(self.vel_esquerda, self.velocidade_base * 3)
        self.vel_direita = min(self.vel_direita, self.velocidade_base * 3)
        
        # Se ambos os lados detectam obstáculos, reduz velocidade geral
        if fator_esq > 0.3 and fator_dir > 0.3:
            self.vel_esquerda *= 0.7
            self.vel_direita *= 0.7
        
        self.ultimo_comando = f"Braitenberg: vL={self.vel_esquerda:.1f}, vR={self.vel_direita:.1f}"
    
    def atualizar_posicao(self):
        """Atualiza a posição do robô baseado nas velocidades das rodas"""
        # Cinemática diferencial
        velocidade = (self.vel_esquerda + self.vel_direita) / 2.0
        omega = (self.vel_direita - self.vel_esquerda) / 20.0  # Fator de escala
        
        # Atualiza ângulo
        self.angulo += omega * 0.05
        
        # Atualiza posição
        self.x += velocidade * math.cos(self.angulo) * 0.05
        self.y += velocidade * math.sin(self.angulo) * 0.05
        
        # Mantém dentro da tela (com margem)
        margem = 30
        if self.x < margem:
            self.x = margem
            self.angulo += math.pi/2
        if self.x > LARGURA - margem:
            self.x = LARGURA - margem
            self.angulo += math.pi/2
        if self.y < margem:
            self.y = margem
            self.angulo += math.pi/2
        if self.y > ALTURA - margem:
            self.y = ALTURA - margem
            self.angulo += math.pi/2
    
    def desenhar(self, tela):
        """Desenha o robô, sensores e informações"""
        fonte = pygame.font.SysFont("monospace", 12)
        fonte_valor = pygame.font.SysFont("monospace", 11)
        
        # Desenha raios sensores
        for i, beta in enumerate(self.angulos_sensores):
            ang = self.angulo + beta
            dist = self.leituras_ruidosas[i]
            
            rx = self.x + dist * math.cos(ang)
            ry = self.y + dist * math.sin(ang)
            
            cor = self.cores_sensores[i]
            
            # Raio com transparência simulada
            if dist < self.alcance_maximo:
                pygame.draw.line(tela, cor, (int(self.x), int(self.y)), (int(rx), int(ry)), 2)
                pygame.draw.circle(tela, (255, 255, 255), (int(rx), int(ry)), 4)
                pygame.draw.circle(tela, cor, (int(rx), int(ry)), 2)
            else:
                pygame.draw.line(tela, (50, 50, 50), (int(self.x), int(self.y)), (int(rx), int(ry)), 1)
                pygame.draw.circle(tela, (50, 50, 50), (int(rx), int(ry)), 2)
            
            # Mostra valor do sensor
            tx = self.x + (dist/2) * math.cos(ang) - 15
            ty = self.y + (dist/2) * math.sin(ang) - 10
            
            if dist < self.alcance_maximo:
                texto = f"{int(dist)}px"
                cor_texto = (255, 255, 255)
            else:
                texto = ">250"
                cor_texto = (80, 80, 80)
            
            txt = fonte.render(texto, True, cor_texto)
            tela.blit(txt, (int(tx), int(ty)))
        
        # Corpo do robô
        pos = (int(self.x), int(self.y))
        
        # Anel de emergência (pisca quando ativado)
        if self.leituras_ruidosas[2] < self.limiar_emergencia:
            cor_emergencia = (255, 0, 0) if pygame.time.get_ticks() % 500 < 250 else (200, 50, 50)
            pygame.draw.circle(tela, cor_emergencia, pos, 30, 4)
        
        # Corpo
        pygame.draw.circle(tela, (0, 200, 255), pos, 22)
        pygame.draw.circle(tela, (100, 220, 255), pos, 22, 2)
        
        # Olhos dos sensores
        for i, beta in enumerate(self.angulos_sensores):
            ang = self.angulo + beta
            px = self.x + 25 * math.cos(ang)
            py = self.y + 25 * math.sin(ang)
            pygame.draw.circle(tela, self.cores_sensores[i], (int(px), int(py)), 3)
        
        # Seta de orientação
        fx = self.x + 32 * math.cos(self.angulo)
        fy = self.y + 32 * math.sin(self.angulo)
        pygame.draw.line(tela, (255, 50, 50), pos, (int(fx), int(fy)), 4)
        
        # Centro
        pygame.draw.circle(tela, (255, 255, 255), pos, 5)
        
        # Mostra velocidades no robô
        txt_vel = fonte_valor.render(f"vL:{self.vel_esquerda:.1f} vR:{self.vel_direita:.1f}", True, (200, 200, 200))
        tela.blit(txt_vel, (self.x - 35, self.y + 30))
    
    def verificar_colisao(self, obstaculos):
        """Verifica se o robô colidiu com algum obstáculo"""
        for obs in obstaculos:
            if obs.collidepoint(self.x, self.y):
                return True
        return False

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("LAB 04 - Veículo de Braitenberg (Comportamento de Medo)")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont("monospace", 13)
    fonte_titulo = pygame.font.SysFont("monospace", 15, bold=True)

    # Robô no centro
    robo = RoboBraitenberg(LARGURA/2, ALTURA/2, 0.0)
    
    # Sala cheia de obstáculos
    obstaculos = [
        pygame.Rect(200, 100, 80, 80),
        pygame.Rect(400, 80, 100, 60),
        pygame.Rect(650, 120, 70, 90),
        pygame.Rect(780, 250, 60, 100),
        pygame.Rect(150, 300, 120, 60),
        pygame.Rect(350, 250, 60, 80),
        pygame.Rect(550, 300, 80, 60),
        pygame.Rect(750, 400, 80, 80),
        pygame.Rect(200, 450, 100, 60),
        pygame.Rect(450, 450, 60, 100),
        pygame.Rect(600, 500, 100, 80),
        pygame.Rect(100, 550, 60, 60),
        pygame.Rect(300, 550, 80, 60),
    ]

    rodando = True
    pausado = False
    mostrar_info = True
    colisoes = 0
    frames = 0
    
    # Adiciona alguns obstáculos aleatórios
    for _ in range(5):
        x = random.randint(50, LARGURA-100)
        y = random.randint(50, ALTURA-100)
        w = random.randint(40, 80)
        h = random.randint(40, 80)
        obstaculos.append(pygame.Rect(x, y, w, h))

    print("\n" + "="*60)
    print("LAB 04 - VEÍCULO DE BRAITENBERG (COMPORTAMENTO DE MEDO)")
    print("="*60)
    print("O robô navega evitando obstáculos reativamente")
    print("Sem mapa, sem planejamento, sem objetivo")
    print("Apenas reagindo aos estímulos dos sensores")
    print("="*60 + "\n")

    while rodando:
        relogio.tick(FPS)
        frames += 1
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    pausado = not pausado
                    print(f"{'Pausado' if pausado else 'Continuando'}")
                
                if evento.key == pygame.K_r:
                    robo = RoboBraitenberg(LARGURA/2, ALTURA/2, random.uniform(0, 2*math.pi))
                    colisoes = 0
                    print("Robô resetado!")
                
                if evento.key == pygame.K_i:
                    mostrar_info = not mostrar_info
                
                if evento.key == pygame.K_ESCAPE:
                    rodando = False

        if not pausado:
            # 1. Calcula sensores
            robo.calcular_sensores(obstaculos)
            
            # 2. Aplica controle de Braitenberg
            robo.controle_braitenberg()
            
            # 3. Atualiza posição
            robo.atualizar_posicao()
            
            # 4. Verifica colisão
            if robo.verificar_colisao(obstaculos):
                colisoes += 1
                # Empurra o robô para fora
                robo.x += math.cos(robo.angulo) * 20
                robo.y += math.sin(robo.angulo) * 20
                robo.angulo += math.pi/2
                print(f"COLISÃO! Total: {colisoes}")

        # Desenho
        tela.fill((20, 24, 30))
        
        # Desenha paredes da sala
        pygame.draw.rect(tela, (40, 44, 50), (0, 0, LARGURA, ALTURA), 3)
        
        # Desenha obstáculos
        for obs in obstaculos:
            # Sombra
            pygame.draw.rect(tela, (100, 30, 30), obs)
            # Corpo
            pygame.draw.rect(tela, (180, 50, 50), obs)
            pygame.draw.rect(tela, (255, 100, 100), obs, 2)
        
        # Desenha robô
        robo.desenhar(tela)

        # Informações na tela
        if mostrar_info:
            y = 15
            infos = [
                ("LAB 04 - BRAITENBERG (MEDO)", (100, 200, 255)),
                ("", None),
                (f"Status: {'PAUSADO' if pausado else 'NAVEGANDO'}", (255, 215, 0) if not pausado else (255, 100, 100)),
                (f"Comando: {robo.ultimo_comando}", (200, 200, 200)),
                ("", None),
                (f"Vel Esq: {robo.vel_esquerda:.2f}", (255, 200, 100)),
                (f"Vel Dir: {robo.vel_direita:.2f}", (100, 200, 255)),
                ("", None),
                ("SENSORES:", (200, 200, 200)),
            ]
            
            for i, (info, cor) in enumerate(infos):
                if info:
                    if cor:
                        txt = fonte.render(info, True, cor)
                    else:
                        txt = fonte.render(info, True, (220, 220, 220))
                    tela.blit(txt, (15, y + i * 20))
            
            # Mostra leituras dos sensores
            y_base = 15 + len(infos) * 20
            for i, nome in enumerate(robo.nomes_sensores):
                cor = robo.cores_sensores[i]
                dist = robo.leituras_ruidosas[i]
                
                if dist < robo.alcance_maximo:
                    texto = f"{nome}: {dist:.1f}px"
                    if dist < 100:
                        cor_texto = (255, 50, 50)
                    elif dist < 180:
                        cor_texto = (255, 200, 50)
                    else:
                        cor_texto = (50, 255, 50)
                else:
                    texto = f"{nome}: >{robo.alcance_maximo:.0f}px"
                    cor_texto = (80, 80, 80)
                
                txt = fonte.render(texto, True, cor_texto)
                tela.blit(txt, (20, y_base + i * 18))
            
            # Informações adicionais
            y_info = ALTURA - 80
            txt_colisoes = fonte.render(f"Colisões: {colisoes}", True, (255, 100, 100) if colisoes > 0 else (100, 255, 100))
            tela.blit(txt_colisoes, (15, y_info))
            
            txt_emergencia = fonte.render(f"Limiar emergência: {robo.limiar_emergencia}px", True, (255, 200, 100))
            tela.blit(txt_emergencia, (15, y_info + 20))
            
            # Controles
            y_ctrl = ALTURA - 45
            txt_ctrl = fonte.render("[SPACE] Pausar  [R] Resetar  [I] Info  [ESC] Sair", True, (150, 150, 150))
            tela.blit(txt_ctrl, (15, y_ctrl))
        
        pygame.display.flip()
    
    pygame.quit()
    print(f"\nSimulação finalizada. Total de colisões: {colisoes}")

if __name__ == "__main__":
    main()