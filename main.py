import pygame #bibioteca para criar jogos
import threading #biblioteca para criar threads
import time #biblioteca para manipular tempo
import random #biblioteca para gerar números aleatórios

# --- Configurações do Jogo ---
LARGURA, ALTURA = 800, 600 #tamanho da tela
FPS = 60 #frames por segundo
BRANCO = (255, 255, 255) #cor branca
PRETO = (0, 0, 0) #cor preta
VERMELHO = (255, 0, 0) #cor vermelha
AZUL = (0, 0, 255) #cor azul

LARGURA_RAQUETE, ALTURA_RAQUETE = 20, 100 #tamanho das raquetes
RAIO_BOLA = 10 #raio de cada bola

# --- Velocidades ---
VELOCIDADE_RAQUETE = 5 
VELOCIDADE_INICIAL_BOLA = 5

# --- Variáveis Compartilhadas ---
pos_raquete1_y = ALTURA // 2 - ALTURA_RAQUETE // 2 #posição inicial da raquete esquerda
pos_raquete2_y = ALTURA // 2 - ALTURA_RAQUETE // 2 #posição inicial da raquete direita
placar_esquerda = 0 #placar do lado esquerdo
placar_direita = 0 #placar do lado direito

executando = True #flag para controlar a execução do jogo

# --- Locks ---
trava_raquete1 = threading.Lock()
trava_raquete2 = threading.Lock()
trava_placar = threading.Lock()

# --- Lista de bolas (cada uma com thread) ---
bolas = [
    {"x": LARGURA // 2, "y": ALTURA // 2,
     "vx": VELOCIDADE_INICIAL_BOLA, "vy": VELOCIDADE_INICIAL_BOLA,
     "lock": threading.Lock()},
    {"x": LARGURA // 3, "y": ALTURA // 3,
     "vx": -VELOCIDADE_INICIAL_BOLA, "vy": VELOCIDADE_INICIAL_BOLA,
     "lock": threading.Lock()}
]


def thread_raquete(lado_raquete):
    global pos_raquete1_y, pos_raquete2_y, executando
    print(f"--- [INFO] Raquete do lado '{lado_raquete.capitalize()}' iniciada. ---")

    ultimo_log = time.time()

    while executando:
        # Pega posição média das bolas
        media_y = sum([bola["y"] for bola in bolas]) / len(bolas)

        if lado_raquete == "esquerda":
            with trava_raquete1:
                if pos_raquete1_y + ALTURA_RAQUETE / 2 < media_y:
                    pos_raquete1_y += VELOCIDADE_RAQUETE
                elif pos_raquete1_y + ALTURA_RAQUETE / 2 > media_y:
                    pos_raquete1_y -= VELOCIDADE_RAQUETE
                pos_raquete1_y = max(0, min(pos_raquete1_y, ALTURA - ALTURA_RAQUETE))

            if time.time() - ultimo_log > 0.5:
                print(f"[RAQUETE ESQUERDA] Posição Y: {pos_raquete1_y:.2f}")
                ultimo_log = time.time()

        else:  # direita
            with trava_raquete2:
                if pos_raquete2_y + ALTURA_RAQUETE / 2 < media_y:
                    pos_raquete2_y += VELOCIDADE_RAQUETE
                elif pos_raquete2_y + ALTURA_RAQUETE / 2 > media_y:
                    pos_raquete2_y -= VELOCIDADE_RAQUETE
                pos_raquete2_y = max(0, min(pos_raquete2_y, ALTURA - ALTURA_RAQUETE))

            if time.time() - ultimo_log > 0.5:
                print(f"[RAQUETE DIREITA] Posição Y: {pos_raquete2_y:.2f}")
                ultimo_log = time.time()

        time.sleep(1 / FPS)


def thread_bola(idx):
    global placar_esquerda, placar_direita, executando
    bola = bolas[idx]
    print(f"--- [INFO] Bola {idx+1} iniciada. ---")

    ultimo_log = time.time()

    while executando:
        with bola["lock"]:
            bola["x"] += bola["vx"]
            bola["y"] += bola["vy"]

            if time.time() - ultimo_log > 0.5:
                print(f"[BOLA {idx+1}] Posição (X, Y): ({bola['x']:.2f}, {bola['y']:.2f})")
                ultimo_log = time.time()

            # Colisão com as paredes
            if bola["y"] - RAIO_BOLA < 0 or bola["y"] + RAIO_BOLA > ALTURA:
                bola["vy"] *= -1

            # Colisão com raquete esquerda
            if bola["x"] - RAIO_BOLA < LARGURA_RAQUETE:
                with trava_raquete1:
                    if pos_raquete1_y < bola["y"] < pos_raquete1_y + ALTURA_RAQUETE:
                        bola["vx"] *= -1
                        bola["vy"] = random.choice([-1, 1]) * abs(bola["vy"])
                    else:
                        with trava_placar:
                            placar_direita += 1
                        bola["x"], bola["y"] = LARGURA // 2, ALTURA // 2
                        bola["vx"] = VELOCIDADE_INICIAL_BOLA
                        bola["vy"] = random.choice([-1, 1]) * VELOCIDADE_INICIAL_BOLA

            # Colisão com raquete direita
            if bola["x"] + RAIO_BOLA > LARGURA - LARGURA_RAQUETE:
                with trava_raquete2:
                    if pos_raquete2_y < bola["y"] < pos_raquete2_y + ALTURA_RAQUETE:
                        bola["vx"] *= -1
                        bola["vy"] = random.choice([-1, 1]) * abs(bola["vy"])
                    else:
                        with trava_placar:
                            placar_esquerda += 1
                        bola["x"], bola["y"] = LARGURA // 2, ALTURA // 2
                        bola["vx"] = -VELOCIDADE_INICIAL_BOLA
                        bola["vy"] = random.choice([-1, 1]) * VELOCIDADE_INICIAL_BOLA

        time.sleep(1 / FPS)


# --- Inicialização do Pygame ---
pygame.init() # inicializa o pygame
tela = pygame.display.set_mode((LARGURA, ALTURA)) # cria a tela do jogo
pygame.display.set_caption("Pong Multithreaded - 2 Bolas")  # título da janela
relogio = pygame.time.Clock() # controla o tempo
fonte_placar = pygame.font.Font(None, 74) # fonte do placar

# --- Criação e Início das Threads ---
thread_raquete1 = threading.Thread(target=thread_raquete, args=("esquerda",)) # cria a thread da raquete esquerda
thread_raquete2 = threading.Thread(target=thread_raquete, args=("direita",)) # cria a thread da raquete direita
thread_raquete1.start()     # inicia a thread da raquete esquerda
thread_raquete2.start()     # inicia a thread da raquete direita

threads_bolas = [] # lista para armazenar as threads das bolas
for i in range(len(bolas)): # para cada bola na lista de bolas
    t = threading.Thread(target=thread_bola, args=(i,)) # cria a thread da bola
    t.start() # inicia a thread da bola
    threads_bolas.append(t)     # adiciona a thread da bola na lista

# --- Loop Principal do Jogo ---
while executando: # enquanto o jogo estiver executando
    for evento in pygame.event.get():   # para cada evento na fila de eventos
        if evento.type == pygame.QUIT: # se o evento for de saída
            executando = False # para o jogo

    tela.fill(PRETO)

    with trava_raquete1: # trava a raquete esquerda
        pygame.draw.rect(tela, VERMELHO, (0, pos_raquete1_y, LARGURA_RAQUETE, ALTURA_RAQUETE)) # Raquete esquerda

    with trava_raquete2: # trava a raquete direita
        pygame.draw.rect(tela, AZUL, (LARGURA - LARGURA_RAQUETE, pos_raquete2_y, LARGURA_RAQUETE, ALTURA_RAQUETE)) # Raquete direita

    # Desenhar todas as bolas
    for bola in bolas: # para cada bola na lista de bolas
        with bola["lock"]: # trava a bola para evitar condições de corrida
            pygame.draw.circle(tela, BRANCO, (int(bola["x"]), int(bola["y"])), RAIO_BOLA) # desenha a bola

    with trava_placar: # trava o placar
        texto_placar = fonte_placar.render(f"{placar_esquerda}  {placar_direita}", True, BRANCO) # placar
    tela.blit(texto_placar, (LARGURA // 2 - texto_placar.get_width() // 2, 10)) # posição do placar

    pygame.display.flip() # atualiza a tela
    relogio.tick(FPS) # controla os frames por segundo

# --- Finalização ---
pygame.quit() # encerra o pygame
print("--- [INFO] Programa encerrado ---")
