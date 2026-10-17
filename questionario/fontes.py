"""Pergunta 5: opcoes de letra para as legendas (texto branco, calmo, centralizado)."""
import skia
from personagem import personagem, P, S, glow

W, H = 960, 540
GROUND = 470
RED = (255, 45, 60)

def cena(c, titulo, familia, estilo, legenda, tam):
    c.clear(skia.Color(14, 10, 28))
    glow(c, 160, 150, 170, (70, 55, 120)); glow(c, 830, 140, 150, (50, 70, 120))
    c.drawLine(0, GROUND, W, GROUND, skia.Paint(Color=skia.Color(70, 55, 120), StrokeWidth=3))
    glow(c, 330, 330, 220, (255, 240, 220), 35)
    personagem(c, 330, GROUND, 0.55)
    # the villain's neon sign, small, so the captions can be compared next to it
    glow(c, 700, 330, 150, RED, 90)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(600, 300, 800, 360), 10, 10), S(RED, 4))
    f = skia.Font(skia.Typeface(familia, estilo), 30)
    c.drawString("desiste.", 700 - f.measureText("desiste.") / 2, 341, f, P(RED))
    # caption near the top, centred
    f = skia.Font(skia.Typeface(familia, estilo), tam)
    c.drawString(legenda, W / 2 - f.measureText(legenda) / 2, 150, f, P((245, 242, 235)))
    lab = skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 26)
    c.drawString(titulo, 24, 40, lab, P((160, 150, 190)))

N, B = skia.FontStyle.Normal(), skia.FontStyle.Bold()
opcoes = [("A  Montserrat - moderna", "Montserrat", B, "Ele ia começar amanhã.", 46),
          ("B  Lato - suave", "Lato", N, "Ele ia começar amanhã.", 48),
          ("C  Comic Neue - escrita à mão", "Comic Neue", B, "Ele ia começar amanhã.", 48),
          ("D  Courier Prime - máquina de escrever", "Courier Prime", N, "Ele ia começar amanhã.", 44),
          ("E  Roboto Slab - livro", "Roboto Slab", N, "Ele ia começar amanhã.", 46),
          ("F  DejaVu - simples", "DejaVu Sans", N, "Ele ia começar amanhã.", 44)]
grid = skia.Surface(W * 3, H * 2)
with grid as g:
    for i, o in enumerate(opcoes):
        s = skia.Surface(W, H)
        with s as c: cena(c, *o)
        x, y = (i % 3) * W, (i // 3) * H
        g.drawImage(s.makeImageSnapshot(), x, y); g.drawRect(skia.Rect(x, y, x + W, y + H), S((0, 0, 0), 6))
grid.makeImageSnapshot().save('5_fontes.png', skia.kPNG)
