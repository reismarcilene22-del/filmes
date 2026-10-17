"""Parte 1: as seis expressoes e os bracos alcancando pontos exatos."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import skia
import personagem as pg
from desenho import W, H, FUNDO, ROXO, AZUL, BRANCO, VERMELHO, P, S, brilho, fonte

def fundo(c, w, h):
    c.clear(skia.Color(*FUNDO)); brilho(c, w * 0.15, h * 0.3, 300, ROXO); brilho(c, w * 0.85, h * 0.25, 260, AZUL)

def rotulo(c, txt, x, y, tam=40):
    f = fonte(tam); c.drawString(txt, x - f.measureText(txt) / 2, y, f, P((200, 190, 230)))

# Linha 1: expressoes
img = skia.Surface(W, H * 2)
with img as c:
    fundo(c, W, H * 2)
    chao = 900
    c.drawLine(0, chao, W, chao, S(ROXO, 4))
    for i, e in enumerate(pg.EXPRESSOES):
        x = 160 + i * 320
        brilho(c, x, chao - 260, 260, (255, 240, 220), 30)
        pg.desenha(c, pg.Pose(x, chao, 0.62, expressao=e, lagrima=0.5 if e == 'triste' else 0))
        rotulo(c, e, x, chao + 70)
    rotulo(c, "Expressões", W / 2, 120, 70)

    # Linha 2: alcance
    chao = H + 900
    c.drawLine(0, chao, W, chao, S(ROXO, 4))
    rotulo(c, "Mãos e pés em pontos exatos", W / 2, H + 120, 70)
    # (a) segurando uma xicara na altura do quadril
    x = 260; pose = pg.Pose(x, chao, 0.8, expressao='feliz')
    pts = pg.pontos(pose); xic = (x + 135, chao - 210)
    pose.mao_dir = xic
    pg.desenha(c, pose)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(xic[0] - 6, xic[1] - 40, xic[0] + 50, xic[1] + 10), 8, 8), P((120, 140, 200)))
    rotulo(c, "segura a xícara", x + 30, chao + 70)
    # (b) acenando com o braco esquerdo para cima
    x = 760; pose = pg.Pose(x, chao, 0.8, expressao='feliz', mao_esq=(x - 150, chao - 420), olhar=(-0.6, -0.4))
    pg.desenha(c, pose); rotulo(c, "acena", x, chao + 70)
    # (c) agachado, as duas maos no chao
    x = 1200; pose = pg.Pose(x, chao, 0.8, expressao='determinado', agachar=40, mao_esq=(x - 110, chao - 4), mao_dir=(x + 110, chao - 4))
    pg.desenha(c, pose); rotulo(c, "mãos no chão", x, chao + 70)
    # (d) tentando alcancar algo longe demais -> falha registrada
    pg.FALHAS.clear(); pg.ROTULO[0] = 'teste'
    x = 1640; alvo = (x + 200, chao - 560)
    pose = pg.Pose(x, chao, 0.8, expressao='assustado', mao_dir=alvo, olhar=(0.8, -0.6))
    pg.desenha(c, pose)
    c.drawCircle(*alvo, 14, P(VERMELHO)); c.drawCircle(*alvo, 26, S(VERMELHO, 4))
    falha = pg.FALHAS[0] if pg.FALHAS else None
    rotulo(c, f"longe demais: faltou {falha[2]:.0f} px" if falha else "sem falha?", x, chao + 70, 34)

img.makeImageSnapshot().save(os.path.join(os.path.dirname(__file__), 't1_personagem.png'), skia.kPNG)
print("falhas registradas:", pg.FALHAS)
