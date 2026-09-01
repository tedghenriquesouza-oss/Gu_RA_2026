import pygame
import math
import numpy as np

LARGURA, ALTURA = 900, 650
FPS = 60

class RoboNavegador:
    def __init__(self, x, y, angulo=0.0):
        self.x = float(x)
        self.y = float(y)
        self.angulo = float(angulo)
        
        # Velocidades
        self.velocidade_max = 2.5
        self.vel_esquerda = 0.0
        self.vel_direita = 0.0
        
        # Alvo
        self.alvo_x = None
        self.alvo_y = None
        self.alvo_atingido = False
        self.distancia_alvo = 0.0
        self.limiar_chegada = 20.0
        
        # Sensores
        self.angulos_sensores = [
            -math.pi/3,
            -math.pi/6,
            0.0,
            math.pi/6,
            math.pi/3
        ]
        
        self.nomes_sensores = ["Esq Ext", "Esq", "Frente", "Dir", "Dir Ext"]
        self.alcance_maximo = 250.0
        self.leituras = [self.alcance_maximo] * 5
        self.leituras_ruidosas = [self.alcance_maximo] * 5
        
        # LIMIAR MAIS ALTO - detecta obstáculos mais longe
        self.limiar_desvio = 130.0
        self.torque_repulsivo = 0.0
        
        self.cores_sensores = [
            (255, 100, 100),
            (255, 200, 100),
            (255, 255, 100),
            (100, 255, 100),
            (100, 200, 255)
        ]
        
        self.estado_atual = "Esperando alvo"
        self.ultimo_comando = ""
        self.colisoes = 0
        
    def definir_alvo(self, x, y):
        self.alvo_x = float(x)
        self.alvo_y = float(y)
        self.alvo_atingido = False
        self.distancia_alvo = self.calcular_distancia_alvo()
        print(f"🎯 Alvo: ({int(x)}, {int(y)}) - Dist: {self.distancia_alvo:.1f}px")
        
    def calcular_distancia_alvo(self):
        if self.alvo_x is None:
            return float('inf')
        dx = self.alvo_x - self.x
        dy = self.alvo_y - self.y
        return math.sqrt(dx*dx + dy*dy)
    
    def calcular_sensores(self, obstaculos):
        self.leituras = []
        self.leituras_ruidosas = []
        
        for beta in self.angulos_sensores:
            ang = self.angulo + beta
            dist = self.alcance_maximo
            
            for passo in range(5, int(self.alcance_maximo), 3):
                rx = self.x + passo * math.cos(ang)
                ry = self.y + passo * math.sin(ang)
                
                if rx <= 0 or rx >= LARGURA or ry <= 0 or ry >= ALTURA:
                    dist = float(passo)
                    break
                
                for obs in obstaculos:
                    if obs.collidepoint(rx, ry):
                        dist = float(passo)
                        break
                if dist < self.alcance_maximo:
                    break
            
            self.leituras.append(dist)
            
            ruido = np.random.normal(0, 2.0)
            dist_ruido = dist + ruido
            
            if dist_ruido > self.alcance_maximo:
                dist_ruido = self.alcance_maximo
            if dist_ruido < 0:
                dist_ruido = 0
                
            self.leituras_ruidosas.append(dist_ruido)
    
    def controle_navegacao(self):
        if self.alvo_x is None:
            self.vel_esquerda = 0
            self.vel_direita = 0
            self.estado_atual = "Sem alvo"
            return
        
        self.distancia_alvo = self.calcular_distancia_alvo()
        
        if self.distancia_alvo < self.limiar_chegada:
            self.alvo_atingido = True
            self.vel_esquerda = 0
            self.vel_direita = 0
            self.estado_atual = "✅ ALVO ATINGIDO!"
            return
        
        # --- VERIFICA EMERGÊNCIA (FRENTE MUITO PERTO) ---
        if self.leituras_ruidosas[2] < 50:
            # Giro no próprio eixo
            self.vel_esquerda = -1.5
            self.vel_direita = 1.5
            self.estado_atual = "🔄 GIRO EMERGÊNCIA"
            return
        
        # --- ATRAÇÃO AO ALVO ---
        dx = self.alvo_x - self.x
        dy = self.alvo_y - self.y
        angulo_alvo = math.atan2(dy, dx)
        
        erro_angulo = angulo_alvo - self.angulo
        erro_angulo = math.atan2(math.sin(erro_angulo), math.cos(erro_angulo))
        
        # Velocidade linear
        vel_linear = min(self.velocidade_max, 0.6 * self.distancia_alvo / 40.0)
        vel_linear = max(vel_linear, 0.3)
        
        # Se tem obstáculo à frente, reduz velocidade
        if self.leituras_ruidosas[2] < self.limiar_desvio:
            fator_seg = max(0.2, self.leituras_ruidosas[2] / self.limiar_desvio)
            vel_linear = vel_linear * fator_seg
        
        # Velocidade angular (proporcional ao erro)
        vel_angular = 0.12 * erro_angulo
        vel_angular = max(-2.0, min(2.0, vel_angular))
        
        # --- DESVIO DE OBSTÁCULOS ---
        torque = 0.0
        desviando = False
        
        # Sensor frontal
        if self.leituras_ruidosas[2] < self.limiar_desvio:
            fator = (self.limiar_desvio - self.leituras_ruidosas[2]) / self.limiar_desvio
            torque += fator * 2.0
            desviando = True
        
        # Sensor esquerdo
        if self.leituras_ruidosas[1] < self.limiar_desvio:
            fator = (self.limiar_desvio - self.leituras_ruidosas[1]) / self.limiar_desvio
            torque -= fator * 1.5
            desviando = True
        
        # Sensor direito
        if self.leituras_ruidosas[3] < self.limiar_desvio:
            fator = (self.limiar_desvio - self.leituras_ruidosas[3]) / self.limiar_desvio
            torque += fator * 1.5
            desviando = True
        
        self.torque_repulsivo = torque
        
        # Combina os controles
        if desviando:
            vel_angular_final = vel_angular + torque
            vel_angular_final = max(-3.0, min(3.0, vel_angular_final))
            vel_linear_final = vel_linear * 0.5
            self.estado_atual = "⚠️ DESVIANDO"
        else:
            vel_angular_final = vel_angular
            vel_linear_final = vel_linear
            self.estado_atual = "➡️ Seguindo alvo"
        
        # Cinemática diferencial
        raio = 12.0
        self.vel_esquerda = vel_linear_final - (vel_angular_final * raio)
        self.vel_direita = vel_linear_final + (vel_angular_final * raio)
        
        max_vel = self.velocidade_max
        self.vel_esquerda = max(-max_vel, min(max_vel, self.vel_esquerda))
        self.vel_direita = max(-max_vel, min(max_vel, self.vel_direita))
    
    def atualizar_posicao(self):
        # CORRIGIDO: fator de escala correto
        velocidade = (self.vel_esquerda + self.vel_direita) / 2.0
        omega = (self.vel_direita - self.vel_esquerda) / 20.0
        
        self.angulo += omega * 0.05
        
        # SEM o * 100.00 que estava quebrando tudo!
        self.x += velocidade * math.cos(self.angulo) * 0.15
        self.y += velocidade * math.sin(self.angulo) * 0.15
        
        # Mantém dentro da tela
        margem = 30
        if self.x < margem:
            self.x = margem
            self.angulo += math.pi/4
        if self.x > LARGURA - margem:
            self.x = LARGURA - margem
            self.angulo += math.pi/4
        if self.y < margem:
            self.y = margem
            self.angulo += math.pi/4
        if self.y > ALTURA - margem:
            self.y = ALTURA - margem
            self.angulo += math.pi/4
    
    def verificar_colisao(self, obstaculos):
        for obs in obstaculos:
            if obs.collidepoint(self.x, self.y):
                return True
        return False
    
    def desenhar(self, tela):
        fonte = pygame.font.SysFont("monospace", 11)
        
        # Desenha raios
        for i, beta in enumerate(self.angulos_sensores):
            ang = self.angulo + beta
            dist = self.leituras_ruidosas[i]
            
            rx = self.x + dist * math.cos(ang)
            ry = self.y + dist * math.sin(ang)
            
            if dist < self.alcance_maximo:
                if dist < self.limiar_desvio:
                    pygame.draw.line(tela, (255, 255, 255), (int(self.x), int(self.y)), (int(rx), int(ry)), 3)
                else:
                    pygame.draw.line(tela, self.cores_sensores[i], (int(self.x), int(self.y)), (int(rx), int(ry)), 2)
                pygame.draw.circle(tela, (255, 255, 255), (int(rx), int(ry)), 4)
            else:
                pygame.draw.line(tela, (40, 40, 40), (int(self.x), int(self.y)), (int(rx), int(ry)), 1)
        
        # Alvo
        if self.alvo_x is not None:
            cor_alvo = (0, 255, 0) if self.alvo_atingido else (255, 215, 0)
            pygame.draw.circle(tela, cor_alvo, (int(self.alvo_x), int(self.alvo_y)), 12, 2)
            pygame.draw.circle(tela, cor_alvo, (int(self.alvo_x), int(self.alvo_y)), 4)
            
            if not self.alvo_atingido:
                pygame.draw.line(tela, (60, 60, 60), (int(self.x), int(self.y)), 
                               (int(self.alvo_x), int(self.alvo_y)), 1)
        
        # Robô
        pos = (int(self.x), int(self.y))
        
        # Anel de emergência
        if self.estado_atual in ["⚠️ DESVIANDO", "🔄 GIRO EMERGÊNCIA"]:
            cor = (255, 0, 0) if pygame.time.get_ticks() % 400 < 200 else (200, 50, 50)
            pygame.draw.circle(tela, cor, pos, 30, 3)
        
        # Corpo
        pygame.draw.circle(tela, (0, 200, 255), pos, 20)
        pygame.draw.circle(tela, (100, 220, 255), pos, 20, 2)
        
        # Olhos dos sensores
        for i, beta in enumerate(self.angulos_sensores):
            ang = self.angulo + beta
            px = self.x + 23 * math.cos(ang)
            py = self.y + 23 * math.sin(ang)
            cor = (255, 255, 255) if self.leituras_ruidosas[i] < self.limiar_desvio else self.cores_sensores[i]
            pygame.draw.circle(tela, cor, (int(px), int(py)), 3)
        
        # Seta
        fx = self.x + 30 * math.cos(self.angulo)
        fy = self.y + 30 * math.sin(self.angulo)
        pygame.draw.line(tela, (255, 50, 50), pos, (int(fx), int(fy)), 4)
        pygame.draw.circle(tela, (255, 255, 255), pos, 4)
        
        # Estado
        fonte_estado = pygame.font.SysFont("monospace", 11, bold=True)
        cores = {
            "✅ ALVO ATINGIDO!": (0, 255, 0),
            "⚠️ DESVIANDO": (255, 200, 0),
            "🔄 GIRO EMERGÊNCIA": (255, 0, 0),
            "➡️ Seguindo alvo": (100, 200, 255),
        }
        cor = cores.get(self.estado_atual, (200, 200, 200))
        txt = fonte_estado.render(self.estado_atual, True, cor)
        tela.blit(txt, (self.x - 40, self.y - 50))

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("LAB 05 - Go-to-Goal com Desvio")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont("monospace", 12)

    robo = RoboNavegador(LARGURA/2, ALTURA/2, 0.0)
    
    obstaculos = [
        pygame.Rect(200, 150, 80, 80),
        pygame.Rect(400, 100, 100, 60),
        pygame.Rect(650, 150, 70, 90),
        pygame.Rect(750, 300, 60, 100),
        pygame.Rect(150, 350, 120, 60),
        pygame.Rect(350, 300, 60, 80),
        pygame.Rect(550, 350, 80, 60),
        pygame.Rect(700, 450, 80, 80),
        pygame.Rect(200, 500, 100, 60),
        pygame.Rect(450, 480, 60, 100),
        pygame.Rect(600, 520, 100, 80),
        pygame.Rect(100, 550, 60, 60),
        pygame.Rect(300, 550, 80, 60),
    ]

    rodando = True
    pausado = False
    
    print("\n" + "="*50)
    print("LAB 05 - NAVEGADOR GO-TO-GOAL")
    print("="*50)
    print("Clique na tela para definir um alvo")
    print("O robô desvia de obstáculos automaticamente")
    print("="*50 + "\n")

    while rodando:
        relogio.tick(FPS)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mx, my = pygame.mouse.get_pos()
                robo.definir_alvo(mx, my)
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    pausado = not pausado
                if evento.key == pygame.K_r:
                    robo = RoboNavegador(LARGURA/2, ALTURA/2, 0.0)
                    robo.colisoes = 0
                    print("Robô resetado!")
                if evento.key == pygame.K_c:
                    robo.alvo_x = None
                    robo.alvo_y = None
                    print("Alvo removido")
                if evento.key == pygame.K_ESCAPE:
                    rodando = False

        if not pausado:
            robo.calcular_sensores(obstaculos)
            robo.controle_navegacao()
            robo.atualizar_posicao()
            
            if robo.verificar_colisao(obstaculos):
                robo.colisoes += 1
                robo.x += math.cos(robo.angulo) * 25
                robo.y += math.sin(robo.angulo) * 25
                print(f"💥 Colisão! Total: {robo.colisoes}")

        # Desenho
        tela.fill((20, 24, 30))
        
        for obs in obstaculos:
            pygame.draw.rect(tela, (100, 30, 30), obs)
            pygame.draw.rect(tela, (180, 50, 50), obs)
            pygame.draw.rect(tela, (255, 100, 100), obs, 2)
        
        robo.desenhar(tela)

        # Interface
        y = 15
        infos = [
            ("LAB 05 - GO-TO-GOAL", (100, 200, 255)),
            ("", None),
            (f"Status: {'PAUSADO' if pausado else 'ATIVO'}", (255, 215, 0) if not pausado else (255, 100, 100)),
            (f"Estado: {robo.estado_atual}", (200, 200, 200)),
            (f"Distância: {robo.distancia_alvo:.1f}px", (255, 200, 100)),
            (f"Colisões: {robo.colisoes}", (255, 100, 100) if robo.colisoes > 0 else (100, 255, 100)),
            ("", None),
            ("SENSORES:", (200, 200, 200)),
        ]
        
        for i, (info, cor) in enumerate(infos):
            if info:
                txt = fonte.render(info, True, cor if cor else (220, 220, 220))
                tela.blit(txt, (15, y + i * 20))
        
        y_base = 15 + len(infos) * 20
        for i, nome in enumerate(robo.nomes_sensores):
            dist = robo.leituras_ruidosas[i]
            if dist < robo.limiar_desvio:
                cor_texto = (255, 0, 0)
                texto = f"{nome}: {dist:.1f}px ⚠️"
            elif dist < 200:
                cor_texto = (255, 200, 50)
                texto = f"{nome}: {dist:.1f}px"
            else:
                cor_texto = (50, 255, 50)
                texto = f"{nome}: >{dist:.0f}px"
            txt = fonte.render(texto, True, cor_texto)
            tela.blit(txt, (20, y_base + i * 18))
        
        # Controles
        txt_ctrl = fonte.render("[Clique] Alvo  [SPACE] Pausar  [R] Resetar  [C] Limpar  [ESC] Sair", True, (100, 100, 100))
        tela.blit(txt_ctrl, (15, ALTURA - 30))

        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()