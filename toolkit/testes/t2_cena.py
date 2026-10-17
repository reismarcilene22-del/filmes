"""Parte 2: quatro momentos de uma mini-cena, com cenario, vilao, legenda, mostrador, camera e acabamento."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import skia
import cena
import personagem as pg
from desenho import W, H

CHAO = 900


def quadro(t):
    s = skia.Surface(W, H)
    with s as c:
        cena.fundo(c, luz=(700, 640))
        cam = cena.Camera(zoom=cena.aproximar(t, 3.0, 6.0, 1.0, 1.08), foco=(W / 2, H / 2 + 40),
                          tremor=1.0 if 4.6 < t < 4.9 else 0.0, t=t)
        c.save(); cam.aplica(c)
        cena.placa(c, 320, 300, 200, 80)
        cena.chao(c, CHAO)
        luz = cena.letreiro(c, 1340, 560, "desiste.", t, acende=1.0)
        expr = 'neutro' if t < 1.2 else ('assustado' if t < 4.6 else 'determinado')
        pg.desenha(c, pg.Pose(700, CHAO, 1.0, expressao=expr, olhar=(0.7 if t > 1.2 else 0, 0)))
        c.restore()
        cena.legenda(c, "Ele ia começar amanhã.", t, 0.0, 2.6)
        cena.legenda(c, "Começa hoje.", t, 5.0, 9.0, destaque=True)
        dia = 1 if t < 4.6 else 2
        cena.mostrador(c, f"DIA {dia}", t, mudou_em=4.6)
    return cena.acabamento(cena.para_rgb(s))


if __name__ == "__main__":
    momentos = [(0.8, "0,8 s: letreiro apagado + legenda"), (1.16, "1,2 s: o vilão acende piscando"),
                (3.4, "3,4 s: aceso, câmera aproximando"), (5.6, "5,6 s: virada, mostrador pulou, frase final")]
    grade = skia.Surface(W, H)
    with grade as g:
        for i, (t, nome) in enumerate(momentos):
            rgb = quadro(t)
            cena.salvar_png(rgb, os.path.join(os.path.dirname(__file__), f"t2_quadro_{i + 1}.png"))
            img = skia.Image.fromarray(np.ascontiguousarray(np.dstack([rgb, np.full((H, W), 255, np.uint8)])),
                                       colorType=skia.kRGBA_8888_ColorType)
            x, y = (i % 2) * W / 2, (i // 2) * H / 2
            g.drawImageRect(img, skia.Rect(x, y, x + W / 2, y + H / 2), skia.SamplingOptions(skia.FilterMode.kLinear))
            f = skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 26)
            g.drawRect(skia.Rect(x, y + H / 2 - 44, x + f.measureText(nome) + 30, y + H / 2), skia.Paint(Color=skia.Color(0, 0, 0, 190)))
            g.drawString(nome, x + 15, y + H / 2 - 13, f, skia.Paint(Color=skia.Color(235, 225, 255), AntiAlias=True))
        g.drawLine(W / 2, 0, W / 2, H, skia.Paint(Color=skia.Color(0, 0, 0), StrokeWidth=6))
        g.drawLine(0, H / 2, W, H / 2, skia.Paint(Color=skia.Color(0, 0, 0), StrokeWidth=6))
    grade.makeImageSnapshot().save(os.path.join(os.path.dirname(__file__), "t2_cena.png"), skia.kPNG)
