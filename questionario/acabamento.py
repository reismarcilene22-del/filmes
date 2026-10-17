"""Pergunta 6: efeitos de acabamento aplicados na mesma cena."""
import numpy as np, skia
from personagem import personagem, P, S, glow

W, H = 960, 540
GROUND = 470
RED = (255, 45, 60)
FONT = 'Comic Neue'

def cena_base():
    s = skia.Surface(W, H)
    with s as c:
        c.clear(skia.Color(14, 10, 28))
        glow(c, 160, 150, 170, (70, 55, 120)); glow(c, 830, 140, 150, (50, 70, 120))
        c.drawRect(skia.Rect(110, 130, 210, 170), S((70, 55, 120), 4))
        c.drawLine(0, GROUND, W, GROUND, skia.Paint(Color=skia.Color(70, 55, 120), StrokeWidth=3))
        glow(c, 330, 330, 220, (255, 240, 220), 35)
        personagem(c, 330, GROUND, 0.55)
        glow(c, 700, 330, 150, RED, 90)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(600, 300, 800, 360), 10, 10), S(RED, 4))
        f = skia.Font(skia.Typeface(FONT, skia.FontStyle.Bold()), 32)
        c.drawString("desiste.", 700 - f.measureText("desiste.") / 2, 341, f, P(RED))
        f = skia.Font(skia.Typeface(FONT, skia.FontStyle.Bold()), 44)
        t = "Ele ia começar amanhã."; c.drawString(t, W / 2 - f.measureText(t) / 2, 150, f, P((245, 242, 235)))
    img = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    return img[:, :, :3].astype(np.float32)

def to_img(a):
    a = np.clip(a, 0, 255).astype(np.uint8)
    rgba = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
    return skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)

def grao(a, forca=0.04):
    rng = np.random.default_rng(1)  # fixed seed: same frame always looks the same
    return a + rng.normal(0, 255 * forca, a.shape[:2])[:, :, None]

def vinheta(a):
    y, x = np.mgrid[0:H, 0:W]; d = np.hypot((x - W / 2) / (W / 2), (y - H / 2) / (H / 2))
    return a * np.clip(1.15 - 0.45 * d ** 2, 0, 1)[:, :, None]

def faixas(a):
    a = a.copy(); b = int(H * 0.09); a[:b] = 0; a[-b:] = 0; return a

def brilho(a):
    from scipy.ndimage import gaussian_filter
    claro = np.clip(a - 160, 0, None)
    return a + gaussian_filter(claro, sigma=(14, 14, 0)) * 1.0

def tv(a):
    a = a.copy(); a[::3] *= 0.6; return a

def rotulo(img, texto):
    s = skia.Surface(W, H)
    with s as c:
        c.drawImage(img, 0, 0)
        f = skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 26)
        c.drawRect(skia.Rect(0, 0, f.measureText(texto) + 40, 52), P((0, 0, 0), 170))
        c.drawString(texto, 20, 36, f, P((235, 225, 255)))
    return s.makeImageSnapshot()

base = cena_base()
opcoes = [("A  Limpo (sem efeito)", base), ("B  Grão de filme", grao(base)), ("C  Vinheta (cantos escuros)", vinheta(base)),
          ("D  Faixas pretas de cinema", faixas(base)), ("E  Brilho neon", brilho(base)), ("F  Linhas de TV antiga", tv(base))]
grid = skia.Surface(W * 3, H * 2)
with grid as g:
    for i, (n, a) in enumerate(opcoes):
        x, y = (i % 3) * W, (i // 3) * H
        g.drawImage(rotulo(to_img(a), n), x, y); g.drawRect(skia.Rect(x, y, x + W, y + H), S((0, 0, 0), 6))
grid.makeImageSnapshot().save('6_acabamento.png', skia.kPNG)
