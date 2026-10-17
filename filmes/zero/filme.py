"""ZERO. — o filme. desenhar(c, t) desenha o instante t; cada cena e uma funcao."""
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, '..', '..', 'toolkit'))
sys.path.insert(0, AQUI)

import skia

import cena
import personagem as pg
import tempos as T
from desenho import W, H, BRANCO, VERMELHO, CREME, P, S, brilho, fonte, suave, mola, entre

CHAO = 900
LUZ_CONTA = (200, 215, 255)       # letreiro de conta aceso: branco-azulado (nem vermelho nem verde)
APAGADO = (52, 44, 78)
POS_SALDO = (1640, 150)
POS_VILAO = (1240, 640)
X_ELE = 440


def dinheiro(v):
    return "R$ " + f"{int(v):,}".replace(",", ".")


# ---------- pecas do cenario ----------

def fila_de_contas():
    """Posicao de cada letreiro na parede, na ordem em que acendem. O ultimo e o GUARDAR."""
    tam, gap = 52, 30
    f, fg = fonte(tam), fonte(30)
    larguras = [f.measureText(nome) + 60 for nome, _ in T.CONTAS] + [fg.measureText("GUARDAR") + 40]
    x = 1870 - sum(larguras) - gap * len(T.CONTAS)          # a fila termina antes da borda direita
    out = []
    for (nome, _), larg in zip(T.CONTAS, larguras):
        out.append((nome, x + larg / 2, 320, larg, tam))
        x += larg + gap
    out.append(("GUARDAR", x + larguras[-1] / 2, 332, larguras[-1], 30))
    return out


def letreiro_conta(c, nome, x, y, larg, tam, luz, cor=LUZ_CONTA):
    alt = tam * 1.6
    caixa = skia.RRect.MakeRectXY(skia.Rect(x - larg / 2, y - alt / 2, x + larg / 2, y + alt / 2), 14, 14)
    f = fonte(tam)
    c.drawRRect(caixa, S(APAGADO, 5))
    c.drawString(nome, x - f.measureText(nome) / 2, y + tam * 0.34, f, P((34, 28, 52)))
    if luz > 0:
        brilho(c, x, y, larg * 0.8, cor, 90 * luz)
        c.drawRRect(caixa, S(cor, 5, 255 * luz))
        c.drawString(nome, x - f.measureText(nome) / 2, y + tam * 0.34, f, P(cor, 255 * luz))


def celular(c, x, y, aceso):
    """Celular na mao, na altura do quadril. Devolve o ponto exato onde a mao segura."""
    if aceso > 0:
        brilho(c, x, y - 20, 120, LUZ_CONTA, 70 * aceso)
    corpo = skia.RRect.MakeRectXY(skia.Rect(x - 20, y - 58, x + 20, y + 10), 7, 7)
    c.drawRRect(corpo, P((40, 36, 60)))
    tela = skia.RRect.MakeRectXY(skia.Rect(x - 15, y - 52, x + 15, y + 4), 4, 4)
    c.drawRRect(tela, P((40 + 170 * aceso, 40 + 180 * aceso, 70 + 185 * aceso)))
    return (x - 4, y - 8)


def moeda_voando(c, de, para, k):
    """Moeda de luz num arco de `de` ate `para` (k de 0 a 1)."""
    if not 0 < k < 1:
        return
    e = suave(k)
    x = de[0] + (para[0] - de[0]) * e
    y = de[1] + (para[1] - de[1]) * e - math.sin(math.pi * e) * 120
    brilho(c, x, y, 90, (255, 240, 200), 170)
    c.drawCircle(x, y, 20, P((255, 245, 220)))


def entrada_da_cena(c, t, inicio):
    """Corte seco, mas o quadro novo sobe do preto em 0,1 s."""
    a = 1 - entre(t, inicio, inicio + 0.1)
    if a > 0:
        c.drawRect(skia.Rect(0, 0, W, H), P((0, 0, 0), 255 * a))


# ---------- cenas 1 e 2: o salario chega e some ----------

def saldo_em(t):
    """Quanto tem no saldo no instante t (cenas 1 e 2). Cada moeda sai do saldo quando comeca a voar."""
    if t < T.SALDO_ENTRA:
        return 0, -10
    v, mudou = T.SALARIO, T.SALDO_ENTRA
    for (nome, valor), acende in zip(T.CONTAS, T.CONTA_ACENDE):
        if t >= acende - T.VOO_MOEDA:
            v -= valor; mudou = acende - T.VOO_MOEDA
    return v, mudou


def cenas_1_e_2(c, t):
    ini = T.CENAS[0][1]
    cena.fundo(c, luz=(X_ELE, 640), luz_forca=0.6 + 0.4 * entre(t, T.PLIM, T.PLIM + 0.3))
    # camera: aproxima devagar na cena 1; na cena 2 abre para mostrar a parede
    if t < 6.0:
        cam = cena.Camera(zoom=cena.aproximar(t, 0, 6, 1.25, 1.32), foco=(X_ELE + 40, 660))   # close nele
    else:
        cam = cena.Camera(zoom=cena.aproximar(t, 6.0, 7.2, 1.0, 1.0), foco=(W / 2, H / 2 + 20))
    c.save(); cam.aplica(c)
    cena.chao(c, CHAO)
    fila = fila_de_contas()
    if t >= 6.0:     # a parede so aparece no plano aberto da cena 2
        for i, (nome, x, y, larg, tam) in enumerate(fila):
            luz = 0.0
            if i < len(T.CONTA_ACENDE) and t >= T.CONTA_ACENDE[i]:
                luz = mola(entre(t, T.CONTA_ACENDE[i], T.CONTA_ACENDE[i] + 0.35))
            letreiro_conta(c, nome, x, y, larg, tam, luz)
        cena.letreiro(c, *POS_VILAO, "esse mês não dá.", t, acende=T.VILAO_NASCE, tamanho=62)

    # personagem
    pose = pg.Pose(X_ELE, CHAO, 1.0, respiracao=math.sin(t * 2.0))
    pose.expressao = 'neutro'
    pose.olhar = (0.5, 0.5)                                # olhando o celular
    if t >= T.SORRI:
        pose.expressao = 'feliz'
    olhou = None
    for i, acende in enumerate(T.CONTA_ACENDE):
        if t >= acende - 0.2:
            olhou = i
    if olhou is not None:
        pose.olhar = (0.9, -0.6)
        pose.expressao = ('neutro', 'neutro', 'triste', 'triste')[olhou]
    if t >= T.VILAO_NASCE + 0.1:
        pose.expressao, pose.olhar = 'triste', (0.8, 0.1)
    if 3.2 < t < 3.3 or 9.4 < t < 9.5:
        pose.piscar = 1.0
    acende_tela = entre(t, T.PLIM, T.PLIM + 0.15) * (1 - 0.5 * entre(t, 12.5, 13.5))
    ponto = celular(c, X_ELE + 95, CHAO - 170, acende_tela)
    pose.mao_dir = ponto
    pg.desenha(c, pose)
    c.restore()

    # moedas voando do saldo ate cada letreiro (em coordenadas de tela: o saldo nao se move com a camera)
    for i, acende in enumerate(T.CONTA_ACENDE):
        _, x, y, _, _ = fila[i]
        moeda_voando(c, (POS_SALDO[0] - 60, POS_SALDO[1] + 20), (x, y), entre(t, acende - T.VOO_MOEDA, acende))

    v, mudou = saldo_em(t)
    if t >= T.SALDO_ENTRA - 0.4:
        cena.mostrador(c, "SALDO " + dinheiro(v), t, mudou_em=mudou, x=POS_SALDO[0], y=POS_SALDO[1],
                       cor=VERMELHO if (v == 0 and t > T.SALDO_ENTRA) else BRANCO)
    cena.legenda(c, "Todo mês, o salário caía.", t, *T.LEGENDA_1)
    cena.legenda(c, "E todo mês, sumia.", t, *T.LEGENDA_2)
    if t >= 6.0:
        entrada_da_cena(c, t, 6.0)


def a_fazer(c, t, nome):
    c.clear(skia.Color(14, 10, 28))
    f = fonte(60)
    txt = f"cena {nome} (a fazer)"
    c.drawString(txt, W / 2 - f.measureText(txt) / 2, H / 2, f, P((120, 110, 160)))


def desenhar(c, t):
    for nome, ini, fim in T.CENAS:
        if ini <= t < fim:
            break
    if t < 17.0:
        cenas_1_e_2(c, t)
    else:
        a_fazer(c, t, nome)


if __name__ == "__main__":
    import render
    pedido = sys.argv[1] if len(sys.argv) > 1 else "folha"
    if pedido == "folha":
        a, b = float(sys.argv[2]), float(sys.argv[3])
        render.folha_de_contato(desenhar, a, b, os.path.join(AQUI, f"folha_{a:05.1f}_{b:05.1f}.png"))
    elif pedido == "contato":
        render.checagem_de_contato(desenhar, T.DURACAO)
    elif pedido == "previa":
        a, b = float(sys.argv[2]), float(sys.argv[3])
        render.render(desenhar, b - a, os.path.join(AQUI, f"previa_{a:05.1f}_{b:05.1f}.mp4"), inicio=a)
    elif pedido == "quadro":
        t = float(sys.argv[2])
        cena.salvar_png(render.quadro(desenhar, t), os.path.join(AQUI, f"quadro_{t:05.2f}.png"))
