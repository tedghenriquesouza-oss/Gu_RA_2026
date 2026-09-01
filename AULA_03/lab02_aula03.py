import pygame
import math
import time

LARGURA, ALTURA = 900, 650
FPS = 60

class Robo:
    def __init__(self, x, y, angulo=0.0):
        self.x = x
        self.y = y
        self.angulo = angulo
        self.angulo_inicial = angulo
        
        # Giro de 90 graus
        self.angulo_para_girar = math.pi / 2
        self.vel_angular = 0.5
        self.tempo_necessario = self.angulo_para_girar / self.vel_angular
        
        self.girando = False
        self.finalizado = False
        self.angulo_final = self.angulo_inicial + self.angulo_para_girar
        self.inicio_tempo = None
        self.zerado = False
        
        # Sensores
        self.angulos_sensores = [-math.pi/4, 0, math.pi/4]
        self.alcance = 150
        self.leituras = [self.alcance, self.alcance, self.alcance]

    def comecar_giro(self):
        self.girando = True
        self.finalizado = False
        self.inicio_tempo = time.time()
        self.zerado = False
        print("\n INICIANDO GIRO DE 90 GRAUS ")
        print(f"Angulo inicial: {math.degrees(self.angulo_inicial):.1f} graus")
        print(f"Tempo estimado: {self.tempo_necessario:.2f} segundos")

    def atualizar(self):
        if not self.girando or self.finalizado:
            return

        tempo_passou = time.time() - self.inicio_tempo

        if tempo_passou < self.tempo_necessario:
            self.angulo = self.angulo_inicial + self.vel_angular * tempo_passou
        else:
            self.angulo = self.angulo_final
            self.girando = False
            self.finalizado = True
            print("\n FINALIZADO")
            print(f"Angulo final: {math.degrees(self.angulo):.1f} graus")
            print(f"Posicao: ({self.x:.1f}, {self.y:.1f}) - MANTIDA!")
            self.zerar()

    def zerar(self):
        if not self.zerado:
            self.zerado = True
            print("\n VELOCIDADE ZERADA ")
            print("Comando /cmd_vel enviado")
            print("Velocidades: vL = 0, vR = 0")

    def calcular_raios(self, obstaculos):
        self.leituras = []
        for beta in self.angulos_sensores:
            ang = self.angulo + beta
            dist = self.alcance
            
            for passo in range(5, self.alcance, 4):
                rx = self.x + passo * math.cos(ang)
                ry = self.y + passo * math.sin(ang)
                
                if rx <= 0 or rx >= LARGURA or ry <= 0 or ry >= ALTURA:
                    dist = float(passo)
                    break
                
                colidiu = False
                for obs in obstaculos:
                    if obs.collidepoint(rx, ry):
                        dist = float(passo)
                        colidiu = True
                        break
                if colidiu:
                    break
            self.leituras.append(dist)

    def desenhar(self, tela):
        # Raios
        for i, beta in enumerate(self.angulos_sensores):
            ang = self.angulo + beta
            dist = self.leituras[i]
            rx = self.x + dist * math.cos(ang)
            ry = self.y + dist * math.sin(ang)
            
            if dist < self.alcance:
                cor = (255, 200, 0)
            else:
                cor = (0, 255, 100)
            
            pygame.draw.line(tela, cor, (int(self.x), int(self.y)), (int(rx), int(ry)), 2)
            pygame.draw.circle(tela, cor, (int(rx), int(ry)), 4)
        
        # Corpo
        pos = (int(self.x), int(self.y))
        pygame.draw.circle(tela, (0, 200, 255), pos, 18)
        pygame.draw.circle(tela, (100, 220, 255), pos, 18, 2)
        
        # Seta
        fx = self.x + 28 * math.cos(self.angulo)
        fy = self.y + 28 * math.sin(self.angulo)
        pygame.draw.line(tela, (255, 50, 50), pos, (int(fx), int(fy)), 4)
        
        # Angulo
        fonte = pygame.font.SysFont("monospace", 16)
        texto = fonte.render(f"{math.degrees(self.angulo) % 360:.1f} graus", True, (255,255,255))
        tela.blit(texto, (self.x - 40, self.y - 50))

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Lab 02 - Giro de 90 graus")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont("monospace", 14)

    robo = Robo(LARGURA/2, ALTURA/2, 0.0)
    
    obstaculos = [
        pygame.Rect(350, 150, 100, 350),
        pygame.Rect(600, 100, 150, 100),
        pygame.Rect(600, 400, 150, 150)
    ]

    robo.comecar_giro()
    rodando = True

    while rodando:
        relogio.tick(FPS)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    robo = Robo(LARGURA/2, ALTURA/2, 0.0)
                    robo.comecar_giro()
                if evento.key == pygame.K_SPACE:
                    robo.girando = not robo.girando
                    if robo.girando:
                        print("Continuando...")
                    else:
                        print("Pausado")
                if evento.key == pygame.K_ESCAPE:
                    rodando = False

        robo.atualizar()
        robo.calcular_raios(obstaculos)

        tela.fill((20, 24, 30))
        
        for obs in obstaculos:
            pygame.draw.rect(tela, (180, 50, 50), obs)
            pygame.draw.rect(tela, (255, 100, 100), obs, 2)
        
        robo.desenhar(tela)

        # Info na tela
        y = 20
        if robo.finalizado:
            status = "CONCLUIDO"
            cor = (0, 255, 0)
        elif robo.girando:
            status = "GIRANDO"
            cor = (255, 215, 0)
        else:
            status = "PAUSADO"
            cor = (255, 165, 0)
        
        infos = [
            f"STATUS: {status}",
            f"Angulo: {math.degrees(robo.angulo) % 360:.1f} graus",
            f"Alvo: {math.degrees(robo.angulo_final) % 360:.1f} graus",
            f"Pos X: {robo.x:.1f}",
            f"Pos Y: {robo.y:.1f}",
            "",
            "[R] Reiniciar",
            "[SPACE] Pausar",
            "[ESC] Sair"
        ]
        
        for i, info in enumerate(infos):
            if "STATUS:" in info:
                texto = fonte.render(info, True, cor)
            else:
                texto = fonte.render(info, True, (220, 220, 220))
            tela.blit(texto, (20, y + i * 22))

        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()