import pygame
import threading
import time
import random

# --- Configurações do Jogo ---
LARGURA, ALTURA = 800, 600
FPS = 60
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)

LARGURA_RAQUETE, ALTURA_RAQUETE = 20, 100
RAIO_BOLA = 10

# --- Velocidade das Raquetes (Agora iguais!) ---
VELOCIDADE_RAQUETE = 5
VELOCIDADE_INICIAL_BOLA = 5

# --- Variáveis Compartilhadas e Trava (Locks) ---
pos_bola_x, pos_bola_y = LARGURA // 2, ALTURA // 2
pos_raquete1_y = ALTURA // 2 - ALTURA_RAQUETE // 2
pos_raquete2_y = ALTURA // 2 - ALTURA_RAQUETE // 2

vel_bola_x, vel_bola_y = VELOCIDADE_INICIAL_BOLA, VELOCIDADE_INICIAL_BOLA

placar_esquerda = 0
placar_direita = 0

trava_bola = threading.Lock()
trava_raquete1 = threading.Lock()
trava_raquete2 = threading.Lock()
trava_placar = threading.Lock()

def thread_raquete(lado_raquete):
    global pos_raquete1_y, pos_raquete2_y
    print(f"--- [INFO] Raquete do lado '{lado_raquete.capitalize()}' iniciada. ---")

    while True:
        with trava_bola:
            pos_bola_atual_x = pos_bola_x
            pos_bola_atual_y = pos_bola_y

        if lado_raquete == "esquerda":
            # Estratégia: Move apenas se a bola estiver na sua metade do campo
            if pos_bola_atual_x < LARGURA / 2:
                with trava_raquete1:
                    if pos_raquete1_y + ALTURA_RAQUETE / 2 < pos_bola_atual_y:
                        pos_raquete1_y += VELOCIDADE_RAQUETE
                    elif pos_raquete1_y + ALTURA_RAQUETE / 2 > pos_bola_atual_y:
                        pos_raquete1_y -= VELOCIDADE_RAQUETE
                    pos_raquete1_y = max(0, min(pos_raquete1_y, ALTURA - ALTURA_RAQUETE))
                print(f"[RAQUETE ESQUERDA] Posição Y: {pos_raquete1_y:.2f}")
            else:
                print(f"[RAQUETE ESQUERDA] Aguardando a bola na posição Y: {pos_raquete1_y:.2f}")

        else: # "direita"
            # Estratégia: Move apenas se a bola estiver na sua metade do campo
            if pos_bola_atual_x > LARGURA / 2:
                with trava_raquete2:
                    if pos_raquete2_y + ALTURA_RAQUETE / 2 < pos_bola_atual_y:
                        pos_raquete2_y += VELOCIDADE_RAQUETE
                    elif pos_raquete2_y + ALTURA_RAQUETE / 2 > pos_bola_atual_y:
                        pos_raquete2_y -= VELOCIDADE_RAQUETE
                    pos_raquete2_y = max(0, min(pos_raquete2_y, ALTURA - ALTURA_RAQUETE))
                print(f"[RAQUETE DIREITA] Posição Y: {pos_raquete2_y:.2f}")
            else:
                print(f"[RAQUETE DIREITA] Aguardando a bola na posição Y: {pos_raquete2_y:.2f}")
        
        time.sleep(1 / FPS)

def thread_bola():
    global pos_bola_x, pos_bola_y, vel_bola_x, vel_bola_y, placar_esquerda, placar_direita
    print("--- [INFO] Bola iniciada. ---")

    while True:
        with trava_bola:
            pos_bola_x += vel_bola_x
            pos_bola_y += vel_bola_y
            print(f"[BOLA] Posição (X, Y): ({pos_bola_x:.2f}, {pos_bola_y:.2f})")

            # Colisão com as paredes de cima/baixo
            if pos_bola_y - RAIO_BOLA < 0 or pos_bola_y + RAIO_BOLA > ALTURA:
                vel_bola_y *= -1

            # Colisão com raquete esquerda
            if pos_bola_x - RAIO_BOLA < LARGURA_RAQUETE:
                with trava_raquete1:
                    if pos_raquete1_y < pos_bola_y < pos_raquete1_y + ALTURA_RAQUETE:
                        vel_bola_x *= -1
                        vel_bola_y = random.choice([-1, 1]) * abs(vel_bola_y)
                        vel_bola_x = random.choice([VELOCIDADE_INICIAL_BOLA, VELOCIDADE_INICIAL_BOLA + 1])
                    else:
                        with trava_placar:
                            placar_direita += 1
                        pos_bola_x, pos_bola_y = LARGURA // 2, ALTURA // 2
                        vel_bola_x = -VELOCIDADE_INICIAL_BOLA
                        vel_bola_y = random.choice([-1, 1]) * VELOCIDADE_INICIAL_BOLA

            # Colisão com raquete direita
            if pos_bola_x + RAIO_BOLA > LARGURA - LARGURA_RAQUETE:
                with trava_raquete2:
                    if pos_raquete2_y < pos_bola_y < pos_raquete2_y + ALTURA_RAQUETE:
                        vel_bola_x *= -1
                        vel_bola_y = random.choice([-1, 1]) * abs(vel_bola_y)
                        vel_bola_x = random.choice([-VELOCIDADE_INICIAL_BOLA, -(VELOCIDADE_INICIAL_BOLA + 1)])
                    else:
                        with trava_placar:
                            placar_esquerda += 1
                        pos_bola_x, pos_bola_y = LARGURA // 2, ALTURA // 2
                        vel_bola_x = VELOCIDADE_INICIAL_BOLA
                        vel_bola_y = random.choice([-1, 1]) * VELOCIDADE_INICIAL_BOLA
        
        time.sleep(1 / FPS)

# --- Inicialização do Pygame ---
pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pong Multithreaded")
relogio = pygame.time.Clock()
fonte_placar = pygame.font.Font(None, 74)

# --- Criação e Início das Threads ---
thread_raquete1 = threading.Thread(target=thread_raquete, args=("esquerda",))
thread_raquete2 = threading.Thread(target=thread_raquete, args=("direita",))
thread_bola = threading.Thread(target=thread_bola)

thread_raquete1.start()
thread_raquete2.start()
thread_bola.start()

# --- Loop Principal do Jogo (Thread Pygame) ---
executando = True
while executando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False

    tela.fill(PRETO)

    with trava_raquete1:
        pygame.draw.rect(tela, VERMELHO, (0, pos_raquete1_y, LARGURA_RAQUETE, ALTURA_RAQUETE))

    with trava_raquete2:
        pygame.draw.rect(tela, AZUL, (LARGURA - LARGURA_RAQUETE, pos_raquete2_y, LARGURA_RAQUETE, ALTURA_RAQUETE))

    with trava_bola:
        pygame.draw.circle(tela, BRANCO, (int(pos_bola_x), int(pos_bola_y)), RAIO_BOLA)
    
    with trava_placar:
        texto_placar = fonte_placar.render(f"{placar_esquerda}  {placar_direita}", True, BRANCO)
    tela.blit(texto_placar, (LARGURA // 2 - texto_placar.get_width() // 2, 10))

    pygame.display.flip()
    relogio.tick(FPS)

# --- Finalização ---
pygame.quit()