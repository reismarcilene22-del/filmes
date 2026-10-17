"""O personagem escolhido: o boneco simples (cabeca redonda, corpo arredondado, pernas de palito), sem cachecol."""
import skia

W, H = 1920, 1080
BODY = (238, 232, 220); LINE = (150, 140, 190); DARK = (20, 14, 36)

def P(col, a=255): return skia.Paint(Color=skia.Color(*col, a), AntiAlias=True)
def S(col, w): return skia.Paint(Color=skia.Color(*col), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, StrokeCap=skia.Paint.kRound_Cap)
def glow(c, x, y, r, col, a=110):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial((x, y), r, [skia.Color(*col, a), skia.Color(*col, 0)])); c.drawCircle(x, y, r, p)

def personagem(c, x, ground, s=1.0):
    head_y = ground - 380 * s
    body = skia.RRect.MakeRectXY(skia.Rect(x - 68 * s, ground - 260 * s, x + 68 * s, ground - 80 * s), 56 * s, 56 * s)
    for dx in (-28, 28):
        c.drawLine(x + dx * s, ground - 90 * s, x + dx * s, ground, S(BODY, 28 * s))
    c.drawRRect(body, P(BODY)); c.drawRRect(body, S(LINE, 6 * s))
    c.drawCircle(x, head_y, 110 * s, P(BODY)); c.drawCircle(x, head_y, 110 * s, S(LINE, 6 * s))
    for dx in (-28, 28):
        c.drawCircle(x + dx * s, head_y, 12 * s, P(DARK))
    m = skia.Path(); m.moveTo(x - 18 * s, head_y + 36 * s); m.quadTo(x, head_y + 50 * s, x + 18 * s, head_y + 36 * s)
    c.drawPath(m, S(DARK, 6 * s))

if __name__ == "__main__":
    surface = skia.Surface(W, H)
    with surface as c:
        c.clear(skia.Color(14, 10, 28))
        glow(c, 320, 320, 340, (70, 55, 120)); glow(c, 1640, 300, 300, (50, 70, 120))
        c.drawRect(skia.Rect(220, 280, 420, 360), S((70, 55, 120), 8))
        c.drawLine(0, 920, W, 920, skia.Paint(Color=skia.Color(70, 55, 120), StrokeWidth=6))
        glow(c, 960, 600, 460, (255, 240, 220), 40)
        personagem(c, 960, 920)
    surface.makeImageSnapshot().save('questionario/3_personagem_escolhido.png', skia.kPNG)
