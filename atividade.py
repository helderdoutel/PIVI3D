import random
from Elevador import Elevador
from Passageiro import Passageiro
import time
import datetime
import numpy as np
import glfw
import OpenGL
import math
OpenGL.ERROR_CHECKING = False
OpenGL.FULL_LOGGING = True
from OpenGL.GL import *
from OpenGL.GLU import *

verticesOrigem = (
    (0.50, -0.50, -0.50),
    (0.50, 0.50, -0.50),
    (-0.50, 0.50, -0.50),
    (-0.50, -0.50, -0.50),
    (0.50, -0.50, 0.50),
    (0.50, 0.50, 0.50),
    (-0.50, -0.50, 0.50),
    (-0.50, 0.50, 0.50)
)

edges = (
    (0, 1),
    (0, 3),
    (0, 4),
    (2, 1),
    (2, 3),
    (2, 7),
    (6, 3),
    (6, 4),
    (6, 7),
    (5, 1),
    (5, 4),
    (5, 7)
)

pessoaOrigem = (
    (0, -0.5, 0),  # base esquerda superior
    (0.1, -0.5, 0),  # base direita superior
    (0.1, -0.5, 0.1),  # base direita inferior
    (0, -0.5, 0.1),  # base esquerda inferior
    (0.05, 1, 0.1)  # topo
)

pessoaArestas = (
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 0),
    (4, 1),
    (4, 2),
    (4, 3)
)

chaoVertices = (
    (0, -0.5, -50),
    (50, -0.5, -50),
    (50, -0.5, 50),
    (0, -0.5, 50),
)

chaoArestas = (
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
)


def gerar_elevadores(quantidade, espacamento_inicial):
    espacamento = espacamento_inicial
    elevadores = []
    for i in range(quantidade):
        tupla = tuple([(i[0] + espacamento, i[1], i[2])
                       for i in verticesOrigem])
        elevador = Elevador()
        elevador.set_vertices(tupla)
        elevador.set_ultima_partida(datetime.datetime(2018, 1, 1, 8, 0, 0, 0))
        elevador.set_tempo_viagem(datetime.timedelta(minutes=0))
        elevadores.append(elevador)
        # print(tupla)
        espacamento += espacamento_inicial
    return elevadores


def gerar_passageiros(funcionarios_total=1000, max_por_min=30, min_por_min=0, espacamento_inicial=1, elevadores=[]):
    hora_chegada = datetime.datetime(2018, 1, 1, 8, 0, 0, 0)
    # datetime.datetime.now() - datetime.timedelta(minutes=15)
    # hr de chegada individual
    maior_x_elevadores = 0
    menor_x_elevadores = 10000
    for index in range(len(elevadores)):
        maior = max([i[0] for i in elevadores[index].get_vertices()])
        menor = min([i[0] for i in elevadores[index].get_vertices()])
        if maior > maior_x_elevadores:
            maior_x_elevadores = maior
        if menor < menor_x_elevadores:
            menor_x_elevadores = menor
    centro = menor_x_elevadores + ((maior_x_elevadores - menor_x_elevadores) / 2)
    fila = []

    espacamento = espacamento_inicial
    id_passageiro = 0
    while funcionarios_total > 0:
        chegou = (np.random.poisson(max_por_min, 1))[0]
        # random.randint(min_por_min, max_por_min)
        if (funcionarios_total - chegou) < 0:
            chegou = funcionarios_total
        funcionarios_total -= chegou
        if chegou > 0:
            tec = float(60) / float(chegou)
        else:
            tec = 0
        while chegou > 0:
            passageiro = Passageiro(id_passageiro=id_passageiro, hora_chegada=hora_chegada)
            id_passageiro += 1
            tupla = tuple([(i[0] + centro, i[1], i[2] + 10)
                           for i in pessoaOrigem])
            passageiro.set_vertices(tupla)
            espacamento += espacamento
            fila.append(passageiro)
            hora_chegada = hora_chegada + datetime.timedelta(seconds=tec)
            chegou -= 1
        if chegou == 0:
            hora_chegada = hora_chegada + datetime.timedelta(minutes=1)
    return fila


def MoverElevador(index, direcao, velocidade):
    if(direcao):
        elevadores[index].set_vertices(tuple(
            [(i[0], i[1] + velocidade, i[2]) for i in elevadores[index].get_vertices()]))
    else:
        elevadores[index].set_vertices(tuple(
            [(i[0], i[1] - velocidade, i[2]) for i in elevadores[index].get_vertices()]))


def colisao(elevador,pessoa):
    # print(elevador[6][2] )
    # print(elevador[3][2])
    if (pessoa[4][0] >= elevador[6][0] and pessoa[4][0] <= elevador[4][0] and pessoa[4][2] <= elevador[6][2]  and  pessoa[4][2] >= elevador[3][2] ):
        return True
    else:
        return False


def mover_passageiro(index, hora_atual, velocidade=0.83):
    xe, ye, ze = elevadores[fila[index].get_elevador()].get_centro_objeto()
    xp, yp, zp = fila[index].get_centro_objeto()
    distancia = math.sqrt(((xp - xe) ** 2) + ((xp - xe)**2))
    viagens = distancia / velocidade
    velocidade_x = (xp - xe) / viagens
    velocidade_z = (zp - ze) / viagens
    fila[index].set_vertices(
        tuple([(i[0] - velocidade_x, i[1], i[2] - velocidade_z) for i in fila[index].get_vertices()]))
    xe, ye, ze = elevadores[fila[index].get_elevador()].get_centro_objeto()
    xp, yp, zp = fila[index].get_centro_objeto()
    if colisao(elevadores[fila[index].get_elevador()].get_vertices(), fila[index].get_vertices()):
        fila[index].set_hora_elevador(hora_atual)
    elif zp <= ze:
        fila[index].set_hora_elevador(hora_atual)


def Desenhar(hora):
    glBegin(GL_LINES)
    for passageiro in fila:
        if passageiro.esperando(hora):
            for edge in pessoaArestas:
                for vertex in edge:
                    glVertex3fv(passageiro.get_vertices()[vertex])
    # for edge in chaoArestas:
    #     for vertex in edge:
    #             glVertex3fv(chaoVertices[vertex])
    for elevador in elevadores:
        for edge in edges:
            for vertex in edge:
                glVertex3fv(elevador.get_vertices()[vertex])
    glEnd()

elevadores = gerar_elevadores(4, 5)
fila = gerar_passageiros(elevadores=elevadores)


def iniciar_viagem(index, hora_atual, tempo_viagem):
    # quebrar = np.random.choice([0, 1], p=[0.99, 0.01])
    if not elevadores[index].em_viagem(hora_atual):
        esperar = False
        for x in elevadores[index].get_passageiros():
            if fila[x].andando(hora_atual):
                esperar = True
                break
        if not esperar:
            elevadores[index].set_ultima_partida(hora_atual)
            elevadores[index].set_tempo_viagem(tempo_viagem)
            elevadores[index].set_viagens(1)
            elevadores[index].zerar_passageiro()


def main():

    if not glfw.init():
        return
    hora_atual = datetime.datetime(2018, 1, 1, 8, 0, 0, 0)
    window = glfw.create_window(1920, 1080, 'Simulação 3D', None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    gluPerspective(90, (1920 / 1080), 0., 25.0)

    glTranslatef(-15, -5, -15)

    # subidas = [True, True, True, True, True, True]

    velocidade = 0.50
    velocidades = []

    for index in range(len(elevadores)):
        velocidades.append(velocidade)
        # velocidade += 0.10
    flag = 0
    contador = 0
    while not glfw.window_should_close(window):
        for index in range(len(elevadores)):
            tempo_viagem = round(np.random.normal(120, 10, 1)[0])
            tempo_viagem = round(tempo_viagem / 2) * 2
            tempo_viagem = datetime.timedelta(seconds=tempo_viagem)
            if elevadores[index].get_ultima_partida() + elevadores[index].get_tempo_viagem() + datetime.timedelta(minutes=2) <= hora_atual:
                iniciar_viagem(index, hora_atual, tempo_viagem)
            if len(elevadores[index].get_passageiros()) >= 10:
                iniciar_viagem(index, hora_atual, tempo_viagem)
            if elevadores[index].get_ultima_partida() + elevadores[index].get_tempo_viagem() > hora_atual:
                if(elevadores[index].get_ultima_partida() + (elevadores[index].get_tempo_viagem() / 2)) > hora_atual:
                    if index == 0:
                        contador += 1
                    MoverElevador(index, True, velocidades[index])
                else:
                    MoverElevador(index, False, velocidades[index])
        for passageiro in fila:
            if passageiro.esperando(hora_atual) and not passageiro.andando(hora_atual):
                for index in range(len(elevadores)):
                    if not elevadores[index].em_viagem(hora_atual) and len(elevadores[index].get_passageiros()) < 10:
                        passageiro.set_elevador(index)
                        elevadores[index].add_passageiro(passageiro.get_id())
                        break
            if passageiro.andando(hora_atual):
                mover_passageiro(passageiro.get_id(), hora_atual)

        glfw.poll_events()
        glfw.swap_buffers(window)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        Desenhar(hora_atual)
        hora_atual = hora_atual + datetime.timedelta(seconds=1)
    glfw.terminate()

if __name__ == "__main__":
    main()
