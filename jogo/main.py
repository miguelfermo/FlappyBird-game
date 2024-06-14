import pygame 
import os
import random
import asyncio

# Configurações da tela largura e altura
TELA_LARGURA = 500
TELA_ALTURA = 800

# pygame.transform.scale2x: Dobra o tamanho da imagem
# pygame.image.load: Carrega a imagem e salva na variável
IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

# Configurações do jogo (FPS, etc)
pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('arial', 50)

class Passaro:
    IMGS = IMAGENS_PASSARO
    # Animação do passaro
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    # Criando um construtor para a classe Passaro no jogo
    def __init__(self, x, y):
        self.x = x # Posição x do passaro
        self.y = y # Posição y do passaro
        self.angulo = 0 # Angulo de rotação do passaro
        self.velocidade = 0 # Velocidade do passaro
        self.altura = self.y # Altura do passaro
        self.tempo = 0 # Tempo do passaro
        self.contagem_imagem = 0 # Contagem de imagens do passaro
        self.imagem = self.IMGS[0] # Imagem do passaro no inicio
    
    # Método para pular do passaro
    def pular(self):
        # Faz o passaro pular para cima (negativo, pois a tela é invertida)
        self.velocidade = -10.5
        self.tempo = 0  # Tempo de quando o passaro pulou
        self.altura = self.y # Altura do passaro quando ele pulou

    # Método para mover o passaro na tela do jogo
    def mover(self):
        # Calcula o deslocamento
        self.tempo += 1 # Incrementa o tempo do passaro
        deslocamento = 0 + self.velocidade * self.tempo + 1.5 * (self.tempo**2) # Calcula o deslocamento do passaro (fórmula sorvetão: S=So + Vot + (at^2)/2)

        # Restringir o deslocamento
        if deslocamento > 16: # Se o deslocamento for maior que 16 (limite de queda) não deixa o passaro cair mais rápido
            deslocamento = 16 
        elif deslocamento < 0: # Se o deslocamento for menor que 0 (limite de pulo) não deixa o passaro subir mais rápido
            deslocamento -= 2 # Pulo mais alto quando pular
        
        self.y = self.y + deslocamento # Atualiza a posição do passaro

        # Angulo do passaro - Animação
        if deslocamento < 0 or self.y < (self.altura + 50): # Se o passaro estiver subindo ou acima da altura do pulo inicial
            if self.angulo < self.ROTACAO_MAXIMA: # Rotação máxima do passaro rotacionado para cima
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90: # Rotação máxima do passaro rotacionado para baixo
                self.angulo -= self.VELOCIDADE_ROTACAO
    
    # Método para desenhar o passaro na tela do jogo 
    def desenhar(self, tela):
        # Define qual imagem do passaro será usada
        self.contagem_imagem += 1
        # Animação do passaro - Bater asas para que a cada 5 frames (TEMPO_ANIMACAO) a imagem do passaro mude (Abrir e fechar as asas)
        if self.contagem_imagem < self.TEMPO_ANIMACAO: # Se a contagem de imagens for menor que o tempo de animação, então a imagem do passaro é a primeira
            self.imagem = self.IMGS[0] 
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2: # Se a contagem de imagens for menor que o tempo de animação*2(10), então a imagem do passaro é a segunda
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3: # Se a contagem de imagens for menor que o tempo de animação*3(15), então a imagem do passaro é a terceira
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4: # Se a contagem de imagens for menor que o tempo de animação*4(20), então a imagem do passaro é a segunda
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem == self.TEMPO_ANIMACAO*4 + 1: # Se a contagem de imagens for igual ao tempo de animação*4 + 1(21), então a imagem do passaro é a primeira
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0 # Reseta a contagem de imagens
        
        # Se o passaro estiver caindo, não bater asas
        if self.angulo <= -80: # Se o angulo do passaro for menor ou igual a -80, então a imagem do passaro é a segunda
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO*2 # Para que a asas do passaro fiquem fechadas e quando houver um pulo, as asas abram
        
        #--confuso--#
        # Desenha o passaro
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo) # Rotaciona a imagem do passaro de acordo com o angulo do passaro através de rotate(imagem, angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center # Pega o centro da imagem original do passaro para colar a imagem rotacionada no centro
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem) # Cria um retangulo para a imagem rotacionada do passaro e cola ela no centro da imagem original
        tela.blit(imagem_rotacionada, retangulo.topleft) # Cola a imagem rotacionada no centro da imagem original, tela.blit = colar na tela

    # Método para pegar a máscara do passaro (colisão) - Para saber se houve colisão entre o passaro e os canos
    def get_mask(self):
        return pygame.mask.from_surface(self.imagem) # Retorna a máscara da imagem do passaro

class Cano:
    DISTANCIA = 200 # Distância entre os canos
    VELOCIDADE = 5 # Velocidade dos canos

    # Criando um construtor para a classe Cano no jogo, para definir a posição x do cano e a altura do cano
    def __init__(self, x): # Construtor da classe Cano, apenas a posição x do cano, pois a posição y é aleatória
        self.x = x # Posição x do cano 
        self.altura = 0 # Altura do cano
        self.pos_topo = 0 # Posição do cano de cima
        self.pos_base = 0 # Posição do cano de baixo
        # .flip(imagem, horizontal, vertical) - Inverte a imagem, horizontal = False, vertical = True
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True) # Inverte a imagem do cano de cima para ficar de cabeça para baixo 
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450) # Altura aleatória entre 50 e 450 para que o passaro possa passar entre os canos mesmo que o passaro pule ou caia
        self.pos_topo = self.altura - self.CANO_TOPO.get_height() # Posição do cano de cima, get_height() pega a altura da imagem do cano
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE # Movimenta o cano para a esquerda (negativo)

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo)) # Desenha o cano de cima na tela
        tela.blit(self.CANO_BASE, (self.x, self.pos_base)) # Desenha o cano de baixo na tela

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask() # Pega a máscara do passaro (colisão) 
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO) # Pega a máscara do cano de cima (colisão) 
        base_mask = pygame.mask.from_surface(self.CANO_BASE) # Pega a máscara do cano de baixo (colisão)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y)) # Distância entre o cano de cima e o passaro
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y)) # Distância entre o cano de baixo e o passaro

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo) # Ponto de colisão entre o passaro e o cano de cima, para ver se ambos tem um pixel em comum
        base_ponto = passaro_mask.overlap(base_mask, distancia_base) # Ponto de colisão entre o passaro e o cano de baixo, para ver se ambos tem um pixel em comum

        if topo_ponto or base_ponto: # Se houver colisão entre o passaro e o cano de cima ou de baixo
            return True
        else:
            return False

class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width() # Largura da imagem do chão 
    IMAGEM = IMAGEM_CHAO # Imagem do chão

    def __init__(self, y): # Construtor da classe Chao, para definir a posição y do chão
        self.y = y
        self.x1 = 0 # Posição x do chão 1
        self.x2 = 0 + self.LARGURA # Posição x do chão 2

    def mover(self):
        self.x1 -= self.VELOCIDADE # Movimenta o chão 1 para a esquerda
        self.x2 -= self.VELOCIDADE # Movimenta o chão 2 para a esquerda

        if self.x1 + self.LARGURA < 0: # Se o chão 1 sair da tela
            self.x1 = self.x2 + self.LARGURA

        if self.x2 + self.LARGURA < 0: # Se o chão 2 sair da tela
            self.x2 = self.x1 + self.LARGURA 
    
    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))

def desenhar_tela(tela, passaros, canos, chao, pontos): # Função para desenhar a tela do jogo
    tela.blit(IMAGEM_BACKGROUND, (0, 0)) # Desenha o background na tela

    for passaro in passaros: # Para cada passaro na lista de passaros
        passaro.desenhar(tela) # Desenha o passaro na tela
    
    for cano in canos: # Para cada cano na lista de canos
        cano.desenhar(tela) # Desenha os canos na tela

    texto = FONTE_PONTOS.render("Pontuação: " + str(pontos), 1, (255, 255, 255)) # Renderiza o texto da pontuação na tela
    
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10)) # Desenha o texto da pontuação na tela

    chao.desenhar(tela) # Desenha o chão na tela
    pygame.display.update() # Atualiza a tela



# Função principal do jogo
async def main():
    # Inicializa o jogo, passado a largura e a altura da tela de cada elemento do jogo para cada classe e função
    passaros = [Passaro(230, 350)] # Lista de passaros no jogo
    chao = Chao(730) # Objeto chão
    canos = [Cano(700)] # Lista de canos no jogo
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA)) # Tela do jogo
    pontos = 0 # Pontuação do jogo
    relogio = pygame.time.Clock() # Relógio do jogo

    rodando = True # Variável para saber se o jogo está rodando
    while rodando: # Enquanto o jogo estiver rodando
        if pontos >= 0 and pontos < 10:
            x = 25
            relogio.tick(x) # FPS do jogo
        elif pontos >= 10 and pontos < 20:
            x = 27
            relogio.tick(x)
        elif pontos >= 20 and pontos < 30:
            x = 29
            relogio.tick(x)
        elif pontos >= 30 and pontos < 40:
            x = 31
            relogio.tick(x)
        elif pontos >= 40 and pontos < 50:
            x = 33
            relogio.tick(x)
        elif pontos >= 50 and pontos < 100:
            x = 34
            relogio.tick(x)
        elif pontos >= 100:
            x = 40
            relogio.tick(x)
        
        for evento in pygame.event.get(): # Para cada evento no pygame
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN: # Se o evento for pressionar uma tecla
                if evento.key == pygame.K_SPACE: # Se a tecla pressionada for a barra de espaço
                    for passaro in passaros: # Para cada passaro na lista de passaros
                        passaro.pular() # O passaro pula pela funcao pular()
            
        # Movimentação do passaro
        for passaro in passaros:
            passaro.mover()
        
        # Movimentação do chao
        chao.mover()

        # Movimentação dos canos

        adicionar_cano = False
        for cano in canos:
            cano.mover()
            remover_cano = []

            for i, passaro in enumerate(passaros): # Para cada passaro na lista de passaros
                if cano.colidir(passaro): # Se o passaro colidir com o cano
                    passaros.pop(i) # Remove o passaro da lista de passaros
                if not cano.passou and passaro.x > cano.x: # Se o passaro passar pelo cano
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0: # Se o cano sair da tela
                remover_cano.append(cano)

        if adicionar_cano: # Se o cano for adicionado
            pontos += 1 # Incrementa a pontuação
            canos.append(Cano(600)) # Adiciona um novo cano na tela

        for cano in remover_cano:
            canos.remove(cano) # Remove o cano da lista de canos

        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0: # Se o passaro tocar no chão ou no teto
                passaros.pop(i) # Remove o passaro da lista de passaros
        
        await asyncio.sleep(0) # Espera 0 segundos para atualizar a tela
        desenhar_tela(tela, passaros, canos, chao, pontos)

if __name__ == "__main__":
    asyncio.run(main()) # Chama a função main() para rodar o jogo
