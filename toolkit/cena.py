"""Pecas de cena: cenario neon, letreiro do vilao, legendas, mostrador (HUD), camera e acabamento."""
import math

import numpy as np
import skia
from scipy.ndimage import gaussian_filter, zoom

from desenho import (W, H, FUNDO, ROXO, AZUL, BRANCO, VERMELHO, VERDE, P, S, brilho, fonte, suave, mola, entre)


# ---------- cenario ----------

def fundo(c, luz=(960, 600), luz_forca=1.0):
    """Noite neon: fundo escuro, letreiros apagados em roxo e azul, e um foco de luz onde a acao acontece."""
    c.clear(skia.Color(*FUNDO))
    brilho(c, 320, 300, 340, ROXO)
    brilho(c, 1640, 280, 300, AZUL)
    if luz is not None:
        brilho(c, luz[0], luz[1], 460, (255, 240, 220), 38 * luz_forca)


def chao(c, y=900):
    c.drawLine(0, y, W, y, S(ROXO, 5))


def placa(c, x, y, largura, altura, cor=ROXO):
    """Letreiro de ambiente (sempre apagado/fosco, nunca vermelho nem verde)."""
    brilho(c, x, y, max(largura, altura) * 1.2, cor, 70)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x - largura / 2, y - altura / 2, x + largura / 2, y + altura / 2), 14, 14),
                S(cor, 8))


# ---------- vilao ----------

def _pisca(t):
    """Neon acendendo: liga e desliga algumas vezes antes de firmar. Sempre igual (sem aleatorio)."""
    padrao = [(0.00, 0.06, 1), (0.06, 0.14, 0), (0.14, 0.18, 1), (0.18, 0.30, 0), (0.30, 0.34, 0.6), (0.34, 0.40, 0)]
    for a, b, v in padrao:
        if a <= t < b:
            return v
    return 1.0 if t >= 0.40 else 0.0


def letreiro(c, x, y, texto, t, acende=None, apaga=None, tamanho=78):
    """O vilao. Antes de `acende` e um letreiro apagado (tubo escuro); depois pisca e fica vermelho.
    Desenha sempre: o letreiro ja esta na cena antes de o vilao 'nascer' dele."""
    f = fonte(tamanho)
    larg = f.measureText(texto) + tamanho * 1.1
    alt = tamanho * 1.7
    caixa = skia.RRect.MakeRectXY(skia.Rect(x - larg / 2, y - alt / 2, x + larg / 2, y + alt / 2), 24, 24)
    luz = 0.0
    if acende is not None and t >= acende:
        luz = _pisca(t - acende)
        if apaga is not None and t >= apaga:
            luz *= 1 - entre(t, apaga, apaga + 0.4)
        luz *= 0.93 + 0.07 * math.sin(t * 47) * math.sin(t * 13)   # zumbido de neon
    # tubo apagado
    c.drawRRect(caixa, S((48, 34, 56), 8))
    c.drawString(texto, x - f.measureText(texto) / 2, y + tamanho * 0.32, f, P((30, 22, 42)))
    if luz > 0:
        brilho(c, x, y, larg * 0.85, VERMELHO, 120 * luz)
        c.drawRRect(caixa, S(VERMELHO, 8, 255 * luz))
        c.drawString(texto, x - f.measureText(texto) / 2, y + tamanho * 0.32, f, P(VERMELHO, 255 * luz))
    return luz


# ---------- texto ----------

def legenda(c, texto, t, inicio, fim, y=210, tamanho=80, destaque=False, entrada=0.5, saida=0.5):
    """Legenda calma, branca, centralizada no alto. destaque=True: a frase final, em verde e com brilho (usar uma vez)."""
    if t < inicio or t > fim:
        return
    a = min(entre(t, inicio, inicio + entrada), 1 - entre(t, fim - saida, fim))
    a = suave(a)
    f = fonte(tamanho)
    x = W / 2 - f.measureText(texto) / 2
    cor = VERDE if destaque else BRANCO
    if destaque:
        brilho(c, W / 2, y - tamanho * 0.3, f.measureText(texto) * 0.6, VERDE, 70 * a)
    sombra = P((0, 0, 0), 140 * a)
    sombra.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8))
    c.drawString(texto, x, y + 4, f, sombra)
    c.drawString(texto, x, y - (1 - a) * 12, f, P(cor, 255 * a))


def mostrador(c, texto, t, mudou_em=-10.0, x=1700, y=150, cor=BRANCO):
    """Caixinha no canto com um numero (o 'dispositivo' do filme). Da um pulinho quando muda."""
    pulo = 1 + 0.25 * (1 - mola(entre(t, mudou_em, mudou_em + 0.5))) if t >= mudou_em else 1
    f = fonte(54)
    larg = f.measureText(texto) + 60
    c.save()
    c.translate(x, y); c.scale(pulo, pulo)
    caixa = skia.RRect.MakeRectXY(skia.Rect(-larg / 2, -45, larg / 2, 45), 16, 16)
    c.drawRRect(caixa, P((20, 16, 40), 220)); c.drawRRect(caixa, S(cor, 4, 200))
    c.drawString(texto, -f.measureText(texto) / 2, 19, f, P(cor))
    c.restore()


# ---------- camera ----------

class Camera:
    """zoom: 1 = normal, 1.08 = aproximou 8%. foco: ponto que fica no centro. tremor: forca do chacoalhao."""

    def __init__(self, zoom=1.0, foco=(W / 2, H / 2), tremor=0.0, t=0.0):
        self.zoom, self.foco, self.tremor, self.t = zoom, foco, tremor, t

    def aplica(self, c):
        dx = dy = 0.0
        if self.tremor:
            dx = self.tremor * 18 * math.sin(self.t * 71) * math.cos(self.t * 23)
            dy = self.tremor * 14 * math.sin(self.t * 53 + 1.3)
        c.translate(W / 2 + dx, H / 2 + dy)
        c.scale(self.zoom, self.zoom)
        c.translate(-self.foco[0], -self.foco[1])


def aproximar(t, inicio, fim, de=1.0, ate=1.08):
    """Zoom lento e suave entre dois instantes."""
    return de + (ate - de) * suave(entre(t, inicio, fim))


# ---------- acabamento ----------

_yy, _xx = np.mgrid[0:H, 0:W]
_VINHETA = np.clip(1.15 - 0.45 * np.hypot((_xx - W / 2) / (W / 2), (_yy - H / 2) / (H / 2)) ** 2, 0, 1)[:, :, None].astype(np.float32)
del _yy, _xx


def acabamento(rgb):
    """Brilho neon + vinheta. Recebe e devolve uma imagem RGB (uint8, H x W x 3)."""
    a = rgb.astype(np.float32)
    pequeno = a.reshape(H // 4, 4, W // 4, 4, 3).mean(axis=(1, 3))          # brilho calculado em 1/4 do tamanho: rapido
    claro = gaussian_filter(np.clip(pequeno - 170, 0, None), sigma=(7, 7, 0))
    a += zoom(claro, (4, 4, 1), order=1) * 0.7
    a *= _VINHETA
    return np.clip(a, 0, 255).astype(np.uint8)


def para_rgb(surface):
    return surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]


def salvar_png(rgb, caminho):
    rgba = np.dstack([rgb, np.full(rgb.shape[:2], 255, np.uint8)])
    skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType).save(caminho, skia.kPNG)
