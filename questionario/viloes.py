"""Pergunta 4: seis ideias de vilao (sempre vermelho, nasce de algo que ja esta na tela)."""
import math, random, skia
from personagem import personagem, P, S, glow

W, H = 960, 540
RED = (255, 45, 60)
GROUND = 470

def cenario(c, titulo):
    c.clear(skia.Color(14, 10, 28))
    glow(c, 160, 150, 170, (70, 55, 120)); glow(c, 830, 140, 150, (50, 70, 120))
    c.drawLine(0, GROUND, W, GROUND, skia.Paint(Color=skia.Color(70, 55, 120), StrokeWidth=3))
    glow(c, 360, 330, 220, (255, 240, 220), 35)
    c.drawString(titulo, 30, 55, skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 34), P((220, 210, 240)))

def sussurro(c, texto, x, y, tam=30):
    f = skia.Font(skia.Typeface('DejaVu Sans'), tam)
    c.drawString(texto, x - f.measureText(texto) / 2, y, f, P(RED))

def red_eyes(c, x, y, r):
    for dx in (-1, 1):
        c.drawCircle(x + dx * r * 1.6, y, r, P((255, 120, 120)))
        c.drawCircle(x + dx * r * 1.6, y, r * 0.45, P((60, 0, 10)))

def sombra(c):
    cenario(c, "A  A própria sombra")
    c.drawRect(skia.Rect(0, 80, W, GROUND), P((22, 16, 40)))  # wall
    sh = skia.Path(); sh.addCircle(600, 180, 95); sh.addRRect(skia.RRect.MakeRectXY(skia.Rect(530, 270, 670, GROUND), 60, 60))
    glow(c, 600, 260, 230, RED, 70); c.drawPath(sh, P(RED, 150))
    red_eyes(c, 600, 175, 11)
    personagem(c, 360, GROUND, 0.55); sussurro(c, "você não está pronto.", 600, 520)

def fumaca(c):
    cenario(c, "B  Fumaça do celular")
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(520, GROUND - 14, 590, GROUND), 6, 6), P((200, 200, 220))); c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(526, GROUND - 11, 584, GROUND - 3), 3, 3), P(RED))
    r = random.Random(4)
    for i in range(14):
        t = i / 13; x = 555 + math.sin(t * 7) * 40 * t; y = GROUND - 20 - t * 300
        glow(c, x, y, 30 + t * 50, RED, int(150 * (1 - t * 0.4)))
    red_eyes(c, 560, 200, 10)
    personagem(c, 360, GROUND, 0.55); sussurro(c, "só mais 5 minutos.", 650, 120)

def olhos(c):
    cenario(c, "C  Olhos no escuro")
    r = random.Random(7)
    for _ in range(9):
        x, y = r.choice([r.uniform(60, 240), r.uniform(500, 920)]), r.uniform(100, 420)
        glow(c, x, y, 40, RED, 70); red_eyes(c, x, y, r.uniform(5, 10))
    personagem(c, 360, GROUND, 0.55); sussurro(c, "todo mundo está olhando.", 480, 515)

def letreiro(c):
    cenario(c, "D  O letreiro neon")
    glow(c, 650, 170, 200, RED, 120)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(500, 120, 800, 220), 14, 14), S(RED, 6))
    f = skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 44)
    t = "desiste."; c.drawString(t, 650 - f.measureText(t) / 2, 186, f, P(RED))
    personagem(c, 360, GROUND, 0.55)

def rabisco(c):
    cenario(c, "E  Nuvem de rabiscos")
    r = random.Random(2); p = skia.Path(); x, y = 360, 170; p.moveTo(x, y)
    for _ in range(90):
        x = min(max(x + r.uniform(-40, 40), 250), 470); y = min(max(y + r.uniform(-25, 25), 110), 210); p.lineTo(x, y)
    glow(c, 360, 165, 180, RED, 60); c.drawPath(p, S(RED, 3))
    personagem(c, 360, GROUND, 0.55); sussurro(c, "e se der errado?", 700, 130)

def glitch(c):
    cenario(c, "F  Glitch / rachadura")
    r = random.Random(5); p = skia.Path(); x, y = 620, 60; p.moveTo(x, y)
    for _ in range(9):
        x += r.uniform(-60, 60); y += r.uniform(30, 50); p.lineTo(x, y)
    glow(c, 620, 260, 200, RED, 70); c.drawPath(p, S(RED, 7))
    for _ in range(7):
        yy = r.uniform(100, 440); c.drawRect(skia.Rect(r.uniform(520, 700), yy, r.uniform(720, 900), yy + r.uniform(4, 12)), P(RED, 160))
    personagem(c, 360, GROUND, 0.55); sussurro(c, "você sempre estraga tudo.", 640, 515)

if __name__ == "__main__":
    opcoes = [sombra, fumaca, olhos, letreiro, rabisco, glitch]
    grid = skia.Surface(W * 3, H * 2)
    with grid as g:
        for i, fn in enumerate(opcoes):
            s = skia.Surface(W, H)
            with s as c: fn(c)
            x, y = (i % 3) * W, (i // 3) * H
            g.drawImage(s.makeImageSnapshot(), x, y); g.drawRect(skia.Rect(x, y, x + W, y + H), S((0, 0, 0), 6))
    grid.makeImageSnapshot().save('4_viloes.png', skia.kPNG)
